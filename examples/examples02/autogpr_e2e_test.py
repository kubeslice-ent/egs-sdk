#!/usr/bin/env python3
"""
Auto-GPR End-to-End Test Script

This script provides comprehensive testing for Auto-GPR functionality following the test flow:
1. Setup Authentication → Connect to EGS API
2. Setup Infrastructure → Create workspace, templates, and binding (only one template)
3. Verify Templates → Confirm templates are created and accessible 
4. Verify Template Binding → Confirm binding is properly configured (bind only one template)
5. Create Auto GPR → Use EGS SDK to create GPR automatically
6. Verify GPR Status → Track GPR lifecycle until "Successful" or provisioned 
7. Generate Report → Create detailed test report
8. Cleanup (mandatory, clean the template also) → Clean up created resources

Author: EGS SDK Team
Date: 2024
"""

import os
import time
import argparse
import yaml
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import logging

import egs
from egs.exceptions import (
    ApiKeyInvalid, ApiKeyNotFound, WorkspaceAlreadyExists, UnhandledException
)


class AutoGPRE2ETest:
    """
    Comprehensive End-to-End test class for Auto-GPR functionality.
    
    This class follows the exact test flow requested:
    1. Authentication setup
    2. Infrastructure creation (workspace, template, binding)
    3. Template verification
    4. Binding verification  
    5. Auto GPR creation
    6. GPR status tracking
    7. Report generation
    8. Mandatory cleanup
    """
    
    def __init__(self, config_path: str):
        """Initialize the test with configuration."""
        self.config = self._load_config(config_path)
        self.auth = None
        self.test_start_time = datetime.now(timezone.utc)
        
        # Track created resources for cleanup
        self.created_resources = {
            'workspace': None,
            'template': None,
            'binding': None,
            'gpr_id': None,
            'api_keys': []
        }
        
        # Test results tracking
        self.test_results = {
            'authentication': {'status': 'pending', 'message': '', 'timestamp': None},
            'infrastructure_setup': {'status': 'pending', 'message': '', 'timestamp': None},
            'template_verification': {'status': 'pending', 'message': '', 'timestamp': None},
            'binding_verification': {'status': 'pending', 'message': '', 'timestamp': None},
            'auto_gpr_creation': {'status': 'pending', 'message': '', 'timestamp': None},
            'gpr_status_tracking': {'status': 'pending', 'message': '', 'timestamp': None},
            'cleanup': {'status': 'pending', 'message': '', 'timestamp': None}
        }
        
        # Setup logging
        self._setup_logging()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            # Validate required sections
            required_sections = ['workspace', 'gprTemplate', 'templateBinding', 'autoGprTest']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required section in config: {section}")
                    
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading configuration file: {str(e)}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create output directory if it doesn't exist
        output_dir = self.config.get('advanced', {}).get('outputDirectory', 'test_outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup logging with UTF-8 encoding to handle emojis on Windows
        log_file = os.path.join(output_dir, f"autogpr_e2e_test_{self.test_start_time.strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _update_test_result(self, step: str, status: str, message: str):
        """Update test result for a specific step."""
        self.test_results[step] = {
            'status': status,
            'message': message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_env_variable(self, env_name: str) -> str:
        """Get environment variable with error handling."""
        value = os.getenv(env_name)
        if value is None:
            raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
        return value

    # ==========================================
    # Step 1: Setup Authentication
    # ==========================================
    def setup_authentication(self) -> bool:
        """Step 1: Setup Authentication → Connect to EGS API"""
        self.logger.info("🔐 Step 1: Setting up authentication...")
        
        try:
            endpoint = self._get_env_variable('EGS_ENDPOINT')
            api_key = self._get_env_variable('EGS_API_KEY')
            
            self.auth = egs.authenticate(endpoint, api_key, sdk_default=False)
            
            self._update_test_result('authentication', 'success', 'Successfully authenticated with EGS API')
            self.logger.info("✅ Authentication successful")
            return True
            
        except Exception as e:
            error_msg = f"Authentication failed: {str(e)}"
            self._update_test_result('authentication', 'failed', error_msg)
            self.logger.error(f"❌ {error_msg}")
            raise

    # ==========================================
    # Step 2: Setup Infrastructure
    # ==========================================
    def setup_infrastructure(self) -> Tuple[str, str, str]:
        """Step 2: Setup Infrastructure → Create workspace, template, and binding (only one template)"""
        self.logger.info("🏗️ Step 2: Setting up infrastructure...")
        
        try:
            # Create workspace
            workspace_name = self._create_workspace()
            
            # Wait for workspace to be ready
            self.logger.info("⏳ Waiting for workspace to be ready...")
            time.sleep(10)
            
            # Get cluster inventory for template creation
            inventory = self._get_cluster_inventory(workspace_name)
            
            # Create single GPR template
            template_name = self._create_gpr_template(inventory)
            
            # Create template binding
            binding_name = self._create_template_binding(workspace_name, template_name)
            
            self._update_test_result('infrastructure_setup', 'success', 
                                   f'Infrastructure created: workspace={workspace_name}, template={template_name}, binding={binding_name}')
            self.logger.info("✅ Infrastructure setup completed successfully")
            
            return workspace_name, template_name, binding_name
            
        except Exception as e:
            error_msg = f"Infrastructure setup failed: {str(e)}"
            self._update_test_result('infrastructure_setup', 'failed', error_msg)
            self.logger.error(f"❌ {error_msg}")
            raise

    def _create_workspace(self) -> str:
        """Create workspace."""
        workspace_config = self.config['workspace']
        workspace_name = workspace_config['name']
        
        self.logger.info(f"📁 Creating workspace: {workspace_name}")
        
        try:
            created_workspace = egs.create_workspace(
                workspace_name=workspace_name,
                clusters=workspace_config['clusters'],
                namespaces=workspace_config['namespaces'],
                username=workspace_config['username'],
                email=workspace_config['email'],
                authenticated_session=self.auth
            )
            
            self.created_resources['workspace'] = workspace_name
            self.logger.info(f"✅ Workspace created: {created_workspace}")
            return workspace_name
            
        except WorkspaceAlreadyExists:
            self.logger.info(f"⚠️ Workspace {workspace_name} already exists, proceeding...")
            self.created_resources['workspace'] = workspace_name
            return workspace_name
        except Exception as e:
            self.logger.error(f"❌ Failed to create workspace: {str(e)}")
            raise

    def _get_cluster_inventory(self, workspace_name: str) -> Any:
        """Get cluster inventory for template creation."""
        self.logger.info(f"[INVENTORY] Retrieving cluster inventory for workspace: {workspace_name}")
        
        try:
            inventory = egs.workspace_inventory(workspace_name, authenticated_session=self.auth)
            
            if not inventory.workspace_inventory:
                raise ValueError(f"No inventory found for workspace: {workspace_name}")
            
            # Check if config specifies a particular GPU shape
            template_config = self.config['gprTemplate']
            requested_gpu_shape = template_config.get('gpuShape')
            
            selected_inventory = None
            
            if requested_gpu_shape:
                # Look for the requested GPU shape in inventory
                self.logger.info(f"   Looking for requested GPU shape: {requested_gpu_shape}")
                for item in inventory.workspace_inventory:
                    if item.gpu_shape == requested_gpu_shape:
                        selected_inventory = item
                        self.logger.info(f"[SUCCESS] Found requested GPU shape in inventory!")
                        break
                
                if not selected_inventory:
                    # Show available options
                    available_shapes = [item.gpu_shape for item in inventory.workspace_inventory]
                    self.logger.warning(f"[WARNING] Requested GPU shape '{requested_gpu_shape}' not available.")
                    self.logger.info(f"   Available GPU shapes: {available_shapes}")
                    self.logger.info(f"   Falling back to first available: {available_shapes[0]}")
                    selected_inventory = inventory.workspace_inventory[0]
            else:
                # Use the first inventory item (original behavior)
                selected_inventory = inventory.workspace_inventory[0]
            
            self.logger.info(f"[INVENTORY] Selected configuration:")
            self.logger.info(f"   Cluster: {selected_inventory.cluster_name}")
            self.logger.info(f"   GPU Shape: {selected_inventory.gpu_shape}")
            self.logger.info(f"   Instance Type: {selected_inventory.instance_type}")
            self.logger.info(f"   GPUs per Node: {selected_inventory.gpu_per_node}")
            self.logger.info(f"   Memory per GPU: {selected_inventory.memory_per_gpu}GB")
            
            return selected_inventory
            
        except Exception as e:
            self.logger.error(f"[FAILED] Failed to retrieve cluster inventory: {str(e)}")
            raise

    def _create_gpr_template(self, inventory: Any) -> str:
        """Create single GPR template."""
        template_config = self.config['gprTemplate']
        # Generate unique template name with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base_name = template_config['name'].replace('-e2e-template', '').replace('-template', '')
        template_name = f"{base_name}-{timestamp}"
        
        self.logger.info(f"[TEMPLATE] Creating GPR template: {template_name}")
        
        # Use config-specified hardware if available, otherwise fall back to inventory
        gpu_shape = template_config.get('gpuShape', inventory.gpu_shape)
        instance_type = template_config.get('instanceType', inventory.instance_type)
        memory_per_gpu = template_config.get('memoryPerGpu', inventory.memory_per_gpu)
        gpu_per_node = template_config.get('gpuPerNode', inventory.gpu_per_node)
        
        self.logger.info(f"   Using GPU Shape: {gpu_shape}")
        self.logger.info(f"   Using Instance Type: {instance_type}")
        self.logger.info(f"   Using Memory per GPU: {memory_per_gpu}GB")
        self.logger.info(f"   Using GPUs per Node: {gpu_per_node}")
        
        try:
            created_template = egs.create_gpr_template(
                name=template_name,
                cluster_name=template_config['cluster'],
                gpu_per_node_count=gpu_per_node,
                num_gpu_nodes=template_config['numGpuNodes'],
                memory_per_gpu=memory_per_gpu,
                gpu_shape=gpu_shape,
                instance_type=instance_type,
                exit_duration=template_config['exitDuration'],
                priority=template_config['priority'],
                enforce_idle_timeout=template_config['enforceIdleTimeout'],
                enable_eviction=template_config['enableEviction'],
                requeue_on_failure=template_config['requeueOnFailure'],
                idle_timeout_duration=template_config.get('idleTimeoutDuration'),
                authenticated_session=self.auth
            )
            
            self.created_resources['template'] = template_name
            self.logger.info(f"✅ GPR template created: {created_template}")
            return template_name
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create GPR template: {str(e)}")
            raise

    def _create_template_binding(self, workspace_name: str, template_name: str) -> str:
        """Create template binding."""
        binding_config = self.config['templateBinding']
        
        # Update binding config to use the actual template name
        updated_clusters = []
        for cluster in binding_config['clusters']:
            updated_cluster = cluster.copy()
            updated_cluster['defaultTemplateName'] = template_name
            updated_cluster['templates'] = [template_name]
            updated_clusters.append(updated_cluster)
        
        self.logger.info(f"[BINDING] Creating template binding for workspace: {workspace_name}")
        
        try:
            # First, try to delete any existing binding with the same workspace name
            self.logger.info("Checking for existing template bindings...")
            try:
                existing_bindings = egs.list_gpr_template_bindings(self.auth)
                self.logger.info(f"Found {len(existing_bindings.items)} existing bindings")
                
                for binding in existing_bindings.items:
                    self.logger.info(f"Checking binding: {binding.name}")
                    # Check if binding is for our workspace (try different attribute names)
                    workspace_match = False
                    if hasattr(binding, 'workspace_name') and binding.workspace_name == workspace_name:
                        workspace_match = True
                    elif hasattr(binding, 'workspaceName') and binding.workspaceName == workspace_name:  
                        workspace_match = True
                    elif binding.name == workspace_name:  # Sometimes binding name matches workspace name
                        workspace_match = True
                    
                    if workspace_match:
                        self.logger.info(f"WARNING: Found existing binding for workspace, deleting: {binding.name}")
                        egs.delete_gpr_template_binding(binding.name, self.auth)
                        self.logger.info(f"Waiting for deletion to complete...")
                        time.sleep(5)  # Give more time for deletion to complete
                        break
                else:
                    self.logger.info(f"No existing binding found for workspace: {workspace_name}")
                    
            except Exception as cleanup_error:
                self.logger.warning(f"Could not cleanup existing binding: {cleanup_error}")
                # Continue with creation attempt anyway
            
            # Now create the new binding
            self.logger.info(f"Creating new template binding for workspace: {workspace_name}")
            response = egs.create_gpr_template_binding(
                workspace_name=workspace_name,
                clusters=updated_clusters,
                enable_auto_gpr=binding_config['enableAutoGpr'],
                authenticated_session=self.auth
            )
            
            binding_name = response.name
            self.created_resources['binding'] = binding_name
            
            self.logger.info(f"[SUCCESS] Template binding created: {binding_name}")
            self.logger.info(f"   Auto-GPR enabled: {binding_config['enableAutoGpr']}")
            self.logger.info(f"   Bound template: {template_name}")
            
            return binding_name
            
        except Exception as e:
            error_str = str(e)
            # Check if this is an "AlreadyExists" error and try to resolve it
            if "already exists" in error_str.lower() and "409" in error_str:
                self.logger.warning(f"[CONFLICT] Template binding already exists, attempting to delete and recreate...")
                try:
                    # Try to delete the conflicting binding by name (usually same as workspace name)
                    self.logger.info(f"Attempting to delete existing binding: {workspace_name}")
                    egs.delete_gpr_template_binding(workspace_name, self.auth)
                    time.sleep(5)  # Wait for deletion to complete
                    
                    # Retry creation
                    self.logger.info(f"Retrying template binding creation...")
                    response = egs.create_gpr_template_binding(
                        workspace_name=workspace_name,
                        clusters=updated_clusters,
                        enable_auto_gpr=binding_config['enableAutoGpr'],
                        authenticated_session=self.auth
                    )
                    
                    binding_name = response.name
                    self.created_resources['binding'] = binding_name
                    
                    self.logger.info(f"[SUCCESS] Template binding created after retry: {binding_name}")
                    self.logger.info(f"   Auto-GPR enabled: {binding_config['enableAutoGpr']}")
                    self.logger.info(f"   Bound template: {template_name}")
                    
                    return binding_name
                    
                except Exception as retry_error:
                    self.logger.error(f"[FAILED] Retry also failed: {str(retry_error)}")
                    raise
            else:
                self.logger.error(f"[FAILED] Failed to create template binding: {error_str}")
                raise

    # ==========================================
    # Step 3: Verify Templates
    # ==========================================
    def verify_templates(self, template_name: str) -> bool:
        """Step 3: Verify Templates → Confirm templates are created and accessible"""
        self.logger.info("🔍 Step 3: Verifying templates...")
        
        try:
            # List all templates
            templates_response = egs.list_gpr_templates(self.auth)
            template_names = [template.name for template in templates_response.items]
            
            # Check if our template exists
            if template_name not in template_names:
                raise ValueError(f"Template {template_name} not found in list: {template_names}")
            
            # Get specific template details
            template_details = egs.get_gpr_template(template_name, self.auth)
            
            # Verify template configuration
            expected_cluster = self.config['gprTemplate']['cluster']
            if template_details.cluster_name != expected_cluster:
                raise ValueError(f"Template cluster mismatch: expected {expected_cluster}, got {template_details.cluster_name}")
            
            self._update_test_result('template_verification', 'success', 
                                   f'Template verified: {template_name}, cluster: {template_details.cluster_name}')
            self.logger.info("✅ Template verification successful")
            self.logger.info(f"   Template: {template_name}")
            self.logger.info(f"   Cluster: {template_details.cluster_name}")
            self.logger.info(f"   Priority: {template_details.priority}")
            self.logger.info(f"   GPU Nodes: {template_details.number_of_gpu_nodes}")
            
            return True
            
        except Exception as e:
            error_msg = f"Template verification failed: {str(e)}"
            self._update_test_result('template_verification', 'failed', error_msg)
            self.logger.error(f"❌ {error_msg}")
            raise

    # ==========================================
    # Step 4: Verify Template Binding
    # ==========================================
    def verify_template_binding(self, workspace_name: str, binding_name: str, template_name: str) -> bool:
        """Step 4: Verify Template Binding → Confirm binding is properly configured (bind only one template)"""
        self.logger.info("🔗 Step 4: Verifying template binding...")
        
        try:
            # Get binding details
            binding_response = egs.get_gpr_template_binding(binding_name, self.auth)
            
            # Note: GetGprTemplateBindingResponse does not include workspace_name
            # We verify the binding name matches what we created instead
            if binding_response.name != binding_name:
                raise ValueError(f"Binding name mismatch: expected {binding_name}, got {binding_response.name}")
            
            # Verify auto-GPR is enabled
            if not binding_response.enable_auto_gpr:
                raise ValueError("Auto-GPR is not enabled in binding")
            
            # Verify only one template is bound
            expected_template = template_name
            cluster_config = binding_response.clusters[0]
            
            if len(cluster_config.templates) != 1:
                raise ValueError(f"Expected 1 template, found {len(cluster_config.templates)}: {cluster_config.templates}")
            
            if cluster_config.templates[0] != expected_template:
                raise ValueError(f"Template mismatch: expected {expected_template}, got {cluster_config.templates[0]}")
            
            # Use correct attribute name: defaultTemplateName (not default_template_name)
            if cluster_config.defaultTemplateName != expected_template:
                raise ValueError(f"Default template mismatch: expected {expected_template}, got {cluster_config.defaultTemplateName}")
            
            self._update_test_result('binding_verification', 'success', 
                                   f'Binding verified: auto-GPR enabled, single template bound: {expected_template}')
            self.logger.info("✅ Template binding verification successful")
            self.logger.info(f"   Binding Name: {binding_response.name}")
            self.logger.info(f"   Auto-GPR enabled: {binding_response.enable_auto_gpr}")
            self.logger.info(f"   Bound template: {expected_template}")
            self.logger.info(f"   Default template: {cluster_config.defaultTemplateName}")
            
            return True
            
        except Exception as e:
            error_msg = f"Template binding verification failed: {str(e)}"
            self._update_test_result('binding_verification', 'failed', error_msg)
            self.logger.error(f"❌ {error_msg}")
            raise

    # ==========================================
    # Step 5: Create Auto GPR
    # ==========================================
    def create_auto_gpr(self, workspace_name: str, inventory: Any) -> str:
        """Step 5: Create Auto GPR → Use EGS SDK to create GPR automatically"""
        self.logger.info("[AUTO-GPR] Step 5: Creating Auto GPR...")
        
        try:
            auto_gpr_config = self.config['autoGprTest']
            template_config = self.config['gprTemplate']
            
            # Use same hardware specs as template (config-specified or inventory fallback)
            gpu_shape = template_config.get('gpuShape', inventory.gpu_shape)
            instance_type = template_config.get('instanceType', inventory.instance_type)
            memory_per_gpu = template_config.get('memoryPerGpu', inventory.memory_per_gpu)
            gpu_per_node = template_config.get('gpuPerNode', inventory.gpu_per_node)
            
            self.logger.info(f"   Requesting GPU Shape: {gpu_shape}")
            self.logger.info(f"   Requesting Instance Type: {instance_type}")
            self.logger.info(f"   Requesting Memory per GPU: {memory_per_gpu}GB")
            self.logger.info(f"   Requesting GPUs per Node: {gpu_per_node}")
            
            # Create GPR request (this should trigger auto-GPR due to the binding)
            gpr_id = egs.request_gpu(
                request_name=auto_gpr_config['requestName'],
                workspace_name=workspace_name,
                cluster_name=template_config['cluster'],
                node_count=template_config['numGpuNodes'],
                gpu_per_node_count=gpu_per_node,
                memory_per_gpu=memory_per_gpu,
                instance_type=instance_type,
                gpu_shape=gpu_shape,
                exit_duration=auto_gpr_config['exitDuration'],
                priority=auto_gpr_config['priority'],
                idle_timeout_duration=template_config.get('idleTimeoutDuration', "30m"),
                enforce_idle_timeout=template_config['enforceIdleTimeout'],
                enable_eviction=template_config['enableEviction'],
                requeue_on_failure=template_config['requeueOnFailure'],
                authenticated_session=self.auth
            )
            
            self.created_resources['gpr_id'] = gpr_id
            
            self._update_test_result('auto_gpr_creation', 'success', 
                                   f'Auto GPR created successfully: {gpr_id}')
            self.logger.info(f"✅ Auto GPR created successfully")
            self.logger.info(f"   GPR ID: {gpr_id}")
            self.logger.info(f"   Request Name: {auto_gpr_config['requestName']}")
            self.logger.info(f"   Workspace: {workspace_name}")
            
            return gpr_id
            
        except Exception as e:
            error_msg = f"Auto GPR creation failed: {str(e)}"
            self._update_test_result('auto_gpr_creation', 'failed', error_msg)
            self.logger.error(f"❌ {error_msg}")
            raise

    # ==========================================
    # Step 6: Verify GPR Status
    # ==========================================
    def verify_gpr_status(self, gpr_id: str) -> bool:
        """Step 6: Verify GPR Status → Track GPR lifecycle until "Successful" or provisioned"""
        self.logger.info("📊 Step 6: Verifying GPR status and tracking lifecycle...")
        
        try:
            auto_gpr_config = self.config['autoGprTest']
            timeout_seconds = auto_gpr_config.get('timeoutSeconds', 600)
            monitoring_interval = auto_gpr_config.get('monitoringIntervalSeconds', 15)
            expected_states = self.config.get('advanced', {}).get('expectedGprStates', 
                                                                  ['Pending', 'Queued', 'Provisioning', 'Successful'])
            
            start_time = time.time()
            lifecycle_states = []
            
            self.logger.info(f"🔄 Starting GPR status monitoring (timeout: {timeout_seconds}s)")
            
            while time.time() - start_time < timeout_seconds:
                try:
                    # Get GPR status
                    gpr_status = egs.gpu_request_status(gpr_id, self.auth)
                    current_status = gpr_status.status.provisioning_status
                    
                    # Track state if new
                    if not lifecycle_states or lifecycle_states[-1] != current_status:
                        lifecycle_states.append(current_status)
                        self.logger.info(f"   📈 GPR Status: {current_status}")
                        
                        if gpr_status.status.failure_reason:
                            self.logger.warning(f"   ⚠️ Failure reason: {gpr_status.status.failure_reason}")
                    
                    # Check if GPR is successful or provisioned
                    if current_status.lower() in ['successful', 'complete', 'provisioned']:
                        self._update_test_result('gpr_status_tracking', 'success', 
                                               f'GPR reached successful state: {current_status}, lifecycle: {" → ".join(lifecycle_states)}')
                        self.logger.info(f"✅ GPR status verification successful")
                        self.logger.info(f"   Final Status: {current_status}")
                        self.logger.info(f"   Lifecycle: {' → '.join(lifecycle_states)}")
                        if gpr_status.status.num_gpus_allocated:
                            self.logger.info(f"   GPUs Allocated: {gpr_status.status.num_gpus_allocated}")
                        return True
                    
                    # Check for failure states
                    if current_status.lower() in ['failed', 'error', 'cancelled']:
                        error_msg = f"GPR failed with status: {current_status}"
                        if gpr_status.status.failure_reason:
                            error_msg += f", reason: {gpr_status.status.failure_reason}"
                        raise ValueError(error_msg)
                    
                    # Wait before next check
                    time.sleep(monitoring_interval)
                    
                except Exception as status_error:
                    self.logger.warning(f"⚠️ Error getting GPR status: {status_error}")
                    time.sleep(monitoring_interval)
            
            # Timeout reached
            error_msg = f"GPR status verification timed out after {timeout_seconds}s. Last lifecycle: {' → '.join(lifecycle_states)}"
            self._update_test_result('gpr_status_tracking', 'failed', error_msg)
            self.logger.error(f"❌ {error_msg}")
            return False
            
        except Exception as e:
            error_msg = f"GPR status verification failed: {str(e)}"
            self._update_test_result('gpr_status_tracking', 'failed', error_msg)
            self.logger.error(f"❌ {error_msg}")
            raise

    # ==========================================
    # Step 7: Generate Report
    # ==========================================
    def generate_report(self) -> str:
        """Step 7: Generate Report → Create detailed test report"""
        self.logger.info("📄 Step 7: Generating detailed test report...")
        
        try:
            test_end_time = datetime.now(timezone.utc)
            test_duration = test_end_time - self.test_start_time
            
            # Create report data
            report = {
                'test_metadata': {
                    'test_name': 'Auto-GPR End-to-End Test',
                    'start_time': self.test_start_time.isoformat(),
                    'end_time': test_end_time.isoformat(),
                    'duration_seconds': test_duration.total_seconds(),
                    'config_file': self.config
                },
                'test_results': self.test_results,
                'created_resources': self.created_resources,
                'summary': {
                    'total_steps': len(self.test_results),
                    'successful_steps': len([r for r in self.test_results.values() if r['status'] == 'success']),
                    'failed_steps': len([r for r in self.test_results.values() if r['status'] == 'failed']),
                    'overall_status': 'PASSED' if all(r['status'] == 'success' for r in self.test_results.values()) else 'FAILED'
                }
            }
            
            # Save report to file
            output_dir = self.config.get('advanced', {}).get('outputDirectory', 'test_outputs')
            report_file = os.path.join(output_dir, f"autogpr_e2e_test_report_{self.test_start_time.strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            # Print report summary
            self.logger.info("📊 Test Report Summary:")
            self.logger.info(f"   📅 Duration: {test_duration}")
            self.logger.info(f"   ✅ Successful Steps: {report['summary']['successful_steps']}/{report['summary']['total_steps']}")
            self.logger.info(f"   ❌ Failed Steps: {report['summary']['failed_steps']}/{report['summary']['total_steps']}")
            self.logger.info(f"   🎯 Overall Status: {report['summary']['overall_status']}")
            self.logger.info(f"   📄 Full Report: {report_file}")
            
            return report_file
            
        except Exception as e:
            self.logger.error(f"❌ Report generation failed: {str(e)}")
            raise

    # ==========================================
    # Step 8: Cleanup
    # ==========================================
    def cleanup_resources(self) -> bool:
        """Step 8: Cleanup (mandatory) → Clean up created resources including templates"""
        self.logger.info("🧹 Step 8: Cleaning up created resources (mandatory)...")
        
        cleanup_errors = []
        
        try:
            # Release/Cancel GPR if created
            if self.created_resources['gpr_id']:
                try:
                    gpr_id = self.created_resources['gpr_id']
                    self.logger.info(f"🔄 Releasing/Canceling GPR: {gpr_id}")
                    
                    # Check GPR status to determine if we should cancel or release
                    gpr_status = egs.gpu_request_status(gpr_id, self.auth)
                    current_status = gpr_status.status.provisioning_status.lower()
                    
                    if current_status in ['pending', 'queued']:
                        egs.cancel_gpu_request(gpr_id, self.auth)
                        self.logger.info(f"   ✅ GPR canceled: {gpr_id}")
                    elif current_status in ['successful', 'complete', 'provisioned']:
                        egs.release_gpu(gpr_id, self.auth)
                        self.logger.info(f"   ✅ GPR released: {gpr_id}")
                    else:
                        self.logger.info(f"   ⚠️ GPR in state {current_status}, no action needed: {gpr_id}")
                        
                except Exception as e:
                    error_msg = f"Failed to cleanup GPR {self.created_resources['gpr_id']}: {str(e)}"
                    cleanup_errors.append(error_msg)
                    self.logger.error(f"   ❌ {error_msg}")
            
            # Delete template binding
            if self.created_resources['binding']:
                try:
                    binding_name = self.created_resources['binding']
                    self.logger.info(f"🔗 Deleting template binding: {binding_name}")
                    egs.delete_gpr_template_binding(binding_name, self.auth)
                    self.logger.info(f"   ✅ Template binding deleted: {binding_name}")
                except Exception as e:
                    error_msg = f"Failed to delete binding {self.created_resources['binding']}: {str(e)}"
                    cleanup_errors.append(error_msg)
                    self.logger.error(f"   ❌ {error_msg}")
            
            # Delete GPR template (mandatory as requested)
            if self.created_resources['template']:
                try:
                    template_name = self.created_resources['template']
                    self.logger.info(f"📋 Deleting GPR template: {template_name}")
                    egs.delete_gpr_template(template_name, self.auth)
                    self.logger.info(f"   ✅ GPR template deleted: {template_name}")
                except Exception as e:
                    error_msg = f"Failed to delete template {self.created_resources['template']}: {str(e)}"
                    cleanup_errors.append(error_msg)
                    self.logger.error(f"   ❌ {error_msg}")
            
            # Note: Workspace is typically not deleted as it may contain other resources
            # and workspace deletion is a destructive operation
            if self.created_resources['workspace']:
                self.logger.info(f"   ⚠️ Workspace '{self.created_resources['workspace']}' was created but not deleted (manual cleanup required if needed)")
            
            if cleanup_errors:
                error_msg = f"Cleanup completed with {len(cleanup_errors)} errors: {'; '.join(cleanup_errors)}"
                self._update_test_result('cleanup', 'partial', error_msg)
                self.logger.warning(f"⚠️ {error_msg}")
                return False
            else:
                self._update_test_result('cleanup', 'success', 'All resources cleaned up successfully')
                self.logger.info("✅ Cleanup completed successfully")
                return True
                
        except Exception as e:
            error_msg = f"Cleanup failed: {str(e)}"
            self._update_test_result('cleanup', 'failed', error_msg)
            self.logger.error(f"❌ {error_msg}")
            return False

    # ==========================================
    # Main Test Runner
    # ==========================================
    def run_complete_test(self) -> bool:
        """Run the complete end-to-end test following all 8 steps."""
        self.logger.info("🚀 Starting Auto-GPR End-to-End Test")
        self.logger.info("=" * 80)
        
        workspace_name = None
        template_name = None
        binding_name = None
        gpr_id = None
        inventory = None
        
        try:
            # Step 1: Setup Authentication
            self.setup_authentication()
            
            # Step 2: Setup Infrastructure
            workspace_name, template_name, binding_name = self.setup_infrastructure()
            
            # Get inventory for GPR creation
            inventory = self._get_cluster_inventory(workspace_name)
            
            # Step 3: Verify Templates
            self.verify_templates(template_name)
            
            # Step 4: Verify Template Binding
            self.verify_template_binding(workspace_name, binding_name, template_name)
            
            # Step 5: Create Auto GPR
            gpr_id = self.create_auto_gpr(workspace_name, inventory)
            
            # Step 6: Verify GPR Status
            gpr_success = self.verify_gpr_status(gpr_id)
            
            # Step 7: Generate Report
            report_file = self.generate_report()
            
            # Step 8: Cleanup (mandatory)
            cleanup_success = self.cleanup_resources()
            
            # Final result
            overall_success = gpr_success and cleanup_success
            
            self.logger.info("=" * 80)
            if overall_success:
                self.logger.info("🎉 Auto-GPR End-to-End Test COMPLETED SUCCESSFULLY!")
                self.logger.info(f"📄 Detailed report: {report_file}")
                return True
            else:
                self.logger.error("❌ Auto-GPR End-to-End Test FAILED!")
                self.logger.info(f"📄 Detailed report: {report_file}")
                return False
                
        except Exception as e:
            self.logger.error(f"💥 Test failed with critical error: {str(e)}")
            
            # Attempt cleanup even if test failed
            try:
                self.logger.info("🧹 Attempting cleanup after failure...")
                self.cleanup_resources()
            except Exception as cleanup_error:
                self.logger.error(f"⚠️ Cleanup after failure also failed: {str(cleanup_error)}")
            
            # Generate report even on failure
            try:
                report_file = self.generate_report()
                self.logger.info(f"📄 Failure report: {report_file}")
            except Exception as report_error:
                self.logger.error(f"⚠️ Report generation failed: {str(report_error)}")
            
            return False


def main():
    """Main entry point for the Auto-GPR E2E test."""
    parser = argparse.ArgumentParser(
        description="Auto-GPR End-to-End Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Flow:
1. Setup Authentication → Connect to EGS API
2. Setup Infrastructure → Create workspace, templates, and binding (only one template)
3. Verify Templates → Confirm templates are created and accessible 
4. Verify Template Binding → Confirm binding is properly configured (bind only one template)
5. Create Auto GPR → Use EGS SDK to create GPR automatically
6. Verify GPR Status → Track GPR lifecycle until "Successful" or provisioned 
7. Generate Report → Create detailed test report
8. Cleanup (mandatory) → Clean up created resources including templates

Environment Variables Required:
- EGS_ENDPOINT: EGS API endpoint URL
- EGS_API_KEY: EGS API authentication key
        """
    )
    
    parser.add_argument(
        '--config',
        required=True,
        help='Path to the configuration YAML file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    try:
        # Create and run the test
        test = AutoGPRE2ETest(args.config)
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Run the complete test
        success = test.run_complete_test()
        
        # Exit with appropriate code
        exit_code = 0 if success else 1
        exit(exit_code)
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
