import os
import time
import argparse
import yaml
import json
import http.client
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from typing import Dict, List, Optional, Any

import egs
from egs.exceptions import (
    ApiKeyInvalid, ApiKeyNotFound, WorkspaceAlreadyExists, UnhandledException
)


class AutoGPRE2ETest:
    """
    End-to-end test class for Auto-GPR functionality.
    
    This class provides comprehensive testing for:
    1. Workspace creation
    2. GPR template creation based on cluster inventory
    3. GPR template binding creation with auto-GPR enablement
    4. Validation of the complete setup
    5. Optional cleanup of resources
    """
    
    def __init__(self, config_path: str):
        """Initialize the test with configuration."""
        self.config = self._load_config(config_path)
        self.auth = None
        self.created_resources = {
            'workspace': None,
            'templates': [],
            'bindings': [],
            'api_keys': []
        }
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            # Validate required sections
            required_sections = ['workspace', 'gprTemplates', 'templateBinding']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required section in config: {section}")
                    
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading configuration file: {str(e)}")
    
    def _get_env_variable(self, env_name: str) -> str:
        """Get environment variable or raise error if not set."""
        value = os.getenv(env_name)
        if value is None:
            raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
        return value
    
    def _create_owner_api_key(self) -> str:
        """Create an Owner API Key using EGS_ACCESS_TOKEN."""
        egs_endpoint = self._get_env_variable("EGS_ENDPOINT")
        egs_token = self._get_env_variable("EGS_ACCESS_TOKEN")

        parsed_url = urlparse(egs_endpoint)
        host = parsed_url.netloc
        scheme = parsed_url.scheme
        path = "/api/v1/api-key"

        validity = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")

        req_body = {
            "name": "AutoGPR_E2E_OwnerAPIKey",
            "userName": "admin",
            "description": "Owner API Key for Auto-GPR E2E tests",
            "role": "Owner",
            "validity": validity,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {egs_token}",
        }

        conn = http.client.HTTPSConnection(host) if scheme == "https" else http.client.HTTPConnection(host)

        try:
            conn.request("POST", path, body=json.dumps(req_body), headers=headers)
            resp = conn.getresponse()
            response_data = json.loads(resp.read().decode())

            if resp.status != 200:
                raise ValueError(f"❌ Failed to create Owner API Key: {resp.status} {response_data}")

            owner_api_key = response_data.get("data", {}).get("apiKey")
            if not owner_api_key:
                raise ValueError(f"❌ API key not found in response: {response_data}")

            print("✅ Successfully created Owner API Key for E2E test.")
            return owner_api_key

        except Exception as err:
            raise RuntimeError(f"❌ Error creating API key: {err}")
        finally:
            conn.close()
    
    def setup_authentication(self) -> None:
        """Setup authentication for EGS API."""
        print("🔐 Setting up authentication...")
        
        api_key = os.getenv("EGS_API_KEY")
        access_token = os.getenv("EGS_ACCESS_TOKEN")

        if not api_key:
            if access_token:
                print("🔑 EGS_API_KEY not found. Creating Owner API Key using EGS_ACCESS_TOKEN...")
                api_key = self._create_owner_api_key()
            else:
                raise ValueError("Either EGS_API_KEY or EGS_ACCESS_TOKEN must be set.")

        print("✅ Using API Key for authentication.")
        self.auth = egs.authenticate(
            self._get_env_variable("EGS_ENDPOINT"),
            api_key=api_key,
            sdk_default=False
        )
    
    def create_workspace(self, skip_if_exists: bool = False) -> str:
        """Create workspace if it doesn't exist."""
        workspace_config = self.config['workspace']
        workspace_name = workspace_config['name']
        
        print(f"🏗️  Creating workspace: {workspace_name}")
        
        try:
            workspace_name = egs.create_workspace(
                workspace_config['name'],
                workspace_config['clusters'],
                workspace_config['namespaces'],
                workspace_config['username'],
                workspace_config['email'],
                self.auth,
            )
            print(f"✅ Workspace created successfully: {workspace_name}")
            self.created_resources['workspace'] = workspace_name
            return workspace_name
            
        except WorkspaceAlreadyExists:
            if skip_if_exists:
                print(f"⚠️  Workspace {workspace_name} already exists, skipping creation.")
                return workspace_name
            else:
                raise
        except Exception as e:
            print(f"❌ Failed to create workspace: {str(e)}")
            raise
    
    def get_cluster_inventory(self, workspace_name: str) -> List[Any]:
        """Retrieve cluster inventory for template creation."""
        print(f"📊 Retrieving cluster inventory for workspace: {workspace_name}")
        
        try:
            inventory = egs.workspace_inventory(workspace_name, authenticated_session=self.auth)
            
            if not inventory.workspace_inventory:
                raise ValueError(f"No inventory found for workspace: {workspace_name}")
            
            print(f"✅ Retrieved inventory for {len(inventory.workspace_inventory)} clusters")
            
            for i, inv in enumerate(inventory.workspace_inventory):
                print(f"   Cluster {i+1}: {inv.cluster_name}")
                print(f"     GPU Shape: {inv.gpu_shape}")
                print(f"     Instance Type: {inv.instance_type}")
                print(f"     GPUs per Node: {inv.gpu_per_node}")
                print(f"     Memory per GPU: {inv.memory_per_gpu}GB")
                print(f"     Total GPU Nodes: {inv.total_gpu_nodes}")
            
            return inventory.workspace_inventory
            
        except Exception as e:
            print(f"❌ Failed to retrieve cluster inventory: {str(e)}")
            raise
    
    def create_gpr_templates(self, inventory_list: List[Any]) -> List[str]:
        """Create GPR templates based on cluster inventory and configuration."""
        print("📋 Creating GPR templates...")
        
        created_templates = []
        inventory_by_cluster = {inv.cluster_name: inv for inv in inventory_list}
        
        for template_config in self.config['gprTemplates']:
            template_name = template_config['name']
            cluster_name = template_config['cluster']
            
            if cluster_name not in inventory_by_cluster:
                print(f"⚠️  Cluster {cluster_name} not found in inventory, skipping template {template_name}")
                continue
            
            inventory = inventory_by_cluster[cluster_name]
            
            print(f"   Creating template: {template_name} for cluster: {cluster_name}")
            
            try:
                # Create template using inventory data and config overrides
                response = egs.create_gpr_template(
                    name=template_name,
                    cluster_name=cluster_name,
                    gpu_per_node_count=inventory.gpu_per_node,
                    num_gpu_nodes=template_config.get('numGpuNodes', 1),
                    memory_per_gpu=inventory.memory_per_gpu,
                    gpu_shape=inventory.gpu_shape,
                    instance_type=inventory.instance_type,
                    exit_duration=template_config.get('exitDuration', '1h'),
                    priority=template_config.get('priority', 150),
                    enforce_idle_timeout=template_config.get('enforceIdleTimeout', True),
                    enable_eviction=template_config.get('enableEviction', True),
                    requeue_on_failure=template_config.get('requeueOnFailure', True),
                    idle_timeout_duration=template_config.get('idleTimeoutDuration', '5m'),
                    authenticated_session=self.auth
                )
                
                print(f"   ✅ Template created: {response}")
                created_templates.append(response)
                self.created_resources['templates'].append(response)
                
            except Exception as e:
                print(f"   ❌ Failed to create template {template_name}: {str(e)}")
                raise
        
        print(f"✅ Successfully created {len(created_templates)} GPR templates")
        return created_templates
    
    def create_gpr_template_binding(self, workspace_name: str) -> str:
        """Create GPR template binding to enable auto-GPR."""
        print(f"🔗 Creating GPR template binding for workspace: {workspace_name}")
        
        binding_config = self.config['templateBinding']
        
        try:
            response = egs.create_gpr_template_binding(
                workspace_name=workspace_name,
                clusters=binding_config['clusters'],
                enable_auto_gpr=binding_config.get('enableAutoGpr', True),
                authenticated_session=self.auth
            )
            
            binding_name = response.name
            print(f"✅ Successfully created GPR template binding: {binding_name}")
            print(f"   Auto-GPR enabled: {binding_config.get('enableAutoGpr', True)}")
            print(f"   Clusters configured: {len(binding_config['clusters'])}")
            
            for cluster_config in binding_config['clusters']:
                print(f"     - {cluster_config['clusterName']}: {cluster_config['defaultTemplateName']}")
            
            self.created_resources['bindings'].append(binding_name)
            return binding_name
            
        except Exception as e:
            print(f"❌ Failed to create GPR template binding: {str(e)}")
            raise
    
    def validate_setup(self, workspace_name: str, binding_name: str) -> bool:
        """Validate the complete auto-GPR setup."""
        print("🔍 Validating auto-GPR setup...")
        
        validation_passed = True
        
        try:
            # Validate templates
            print("   Checking GPR templates...")
            templates_response = egs.list_gpr_templates(self.auth)
            created_template_names = set(self.created_resources['templates'])
            existing_template_names = {template.name for template in templates_response.items}
            
            missing_templates = created_template_names - existing_template_names
            if missing_templates:
                print(f"   ❌ Missing templates: {missing_templates}")
                validation_passed = False
            else:
                print(f"   ✅ All {len(created_template_names)} templates found")
            
            # Validate binding
            print("   Checking GPR template binding...")
            binding_response = egs.get_gpr_template_binding(binding_name, self.auth)
            
            if binding_response.workspace_name != workspace_name:
                print(f"   ❌ Binding workspace mismatch: expected {workspace_name}, got {binding_response.workspace_name}")
                validation_passed = False
            
            if not binding_response.enable_auto_gpr:
                print("   ❌ Auto-GPR is not enabled in binding")
                validation_passed = False
            else:
                print("   ✅ Auto-GPR is enabled")
            
            expected_clusters = {cluster['clusterName'] for cluster in self.config['templateBinding']['clusters']}
            actual_clusters = {cluster.cluster_name for cluster in binding_response.clusters}
            
            if expected_clusters != actual_clusters:
                print(f"   ❌ Cluster mismatch: expected {expected_clusters}, got {actual_clusters}")
                validation_passed = False
            else:
                print(f"   ✅ All {len(expected_clusters)} clusters configured correctly")
            
            # Validate each cluster configuration
            for expected_cluster in self.config['templateBinding']['clusters']:
                cluster_name = expected_cluster['clusterName']
                actual_cluster = next((c for c in binding_response.clusters if c.cluster_name == cluster_name), None)
                
                if not actual_cluster:
                    print(f"   ❌ Cluster {cluster_name} not found in binding")
                    validation_passed = False
                    continue
                
                expected_default = expected_cluster['defaultTemplateName']
                if actual_cluster.default_template_name != expected_default:
                    print(f"   ❌ Default template mismatch for {cluster_name}: expected {expected_default}, got {actual_cluster.default_template_name}")
                    validation_passed = False
                
                expected_templates = set(expected_cluster['templates'])
                actual_templates = set(actual_cluster.templates)
                if expected_templates != actual_templates:
                    print(f"   ❌ Template list mismatch for {cluster_name}: expected {expected_templates}, got {actual_templates}")
                    validation_passed = False
            
            if validation_passed:
                print("✅ Auto-GPR setup validation completed successfully!")
                print("\n🎉 Auto-GPR is now enabled and ready to use!")
                print("\nNext steps:")
                print("1. Deploy workloads with GPU requests in application namespaces")
                print("2. Workloads will automatically get scheduling gates")
                print("3. EGS agent will create GPRs using the configured templates")
                print("4. GPRs will be provisioned and scheduling gates removed")
                print("5. Workloads will be scheduled on GPU nodes")
            else:
                print("❌ Auto-GPR setup validation failed!")
            
            return validation_passed
            
        except Exception as e:
            print(f"❌ Validation failed with error: {str(e)}")
            return False
    
    def create_workspace_api_key(self, workspace_name: str) -> Optional[str]:
        """Create an API key for the workspace."""
        workspace_config = self.config['workspace']
        
        try:
            print(f"🔑 Creating API key for workspace: {workspace_name}")
            
            api_key = egs.create_api_key(
                name=f"{workspace_name}-autogpr-key",
                role="Editor",
                validity=workspace_config.get('apiKeyValidity', '2024-12-31'),
                username=workspace_config['username'],
                description=f"Auto-GPR E2E test API key for {workspace_name}",
                workspace_name=workspace_name,
                authenticated_session=self.auth,
            )
            
            # Save API key to file
            os.makedirs("autogpr_outputs", exist_ok=True)
            apikey_path = os.path.join("autogpr_outputs", f"{workspace_name}_apikey.txt")
            with open(apikey_path, 'w', encoding='utf-8') as apikey_file:
                apikey_file.write(api_key)
            
            print(f"✅ API key created and saved to: {apikey_path}")
            self.created_resources['api_keys'].append(api_key)
            return api_key
            
        except Exception as e:
            print(f"⚠️  Failed to create API key for workspace: {str(e)}")
            return None
    
    def cleanup_resources(self) -> None:
        """Clean up created resources."""
        print("🧹 Cleaning up created resources...")
        
        # Delete bindings
        for binding_name in self.created_resources['bindings']:
            try:
                egs.delete_gpr_template_binding(binding_name, self.auth)
                print(f"   ✅ Deleted binding: {binding_name}")
            except Exception as e:
                print(f"   ⚠️  Failed to delete binding {binding_name}: {str(e)}")
        
        # Delete templates
        for template_name in self.created_resources['templates']:
            try:
                egs.delete_gpr_template(template_name, self.auth)
                print(f"   ✅ Deleted template: {template_name}")
            except Exception as e:
                print(f"   ⚠️  Failed to delete template {template_name}: {str(e)}")
        
        # Note: Workspace deletion is typically not done in tests as it may contain other resources
        if self.created_resources['workspace']:
            print(f"   ⚠️  Workspace '{self.created_resources['workspace']}' was created but not deleted (manual cleanup required)")
        
        print("✅ Cleanup completed")
    
    def run_test(self, skip_workspace_creation: bool = False, run_cleanup: bool = False) -> bool:
        """Run the complete end-to-end test."""
        try:
            print("🚀 Starting Auto-GPR End-to-End Test")
            print("=" * 50)
            
            # Setup authentication
            self.setup_authentication()
            
            # Create or use existing workspace
            workspace_name = self.create_workspace(skip_if_exists=skip_workspace_creation)
            
            # Wait for workspace to be ready
            print("⏳ Waiting for workspace to be ready...")
            time.sleep(10)
            
            # Get cluster inventory
            inventory_list = self.get_cluster_inventory(workspace_name)
            
            # Create GPR templates
            created_templates = self.create_gpr_templates(inventory_list)
            
            # Create GPR template binding
            binding_name = self.create_gpr_template_binding(workspace_name)
            
            # Create workspace API key (optional)
            self.create_workspace_api_key(workspace_name)
            
            # Validate setup
            validation_passed = self.validate_setup(workspace_name, binding_name)
            
            if run_cleanup:
                self.cleanup_resources()
            
            print("=" * 50)
            if validation_passed:
                print("🎉 Auto-GPR End-to-End Test PASSED!")
                return True
            else:
                print("❌ Auto-GPR End-to-End Test FAILED!")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            if run_cleanup:
                try:
                    self.cleanup_resources()
                except Exception as cleanup_error:
                    print(f"⚠️  Cleanup also failed: {str(cleanup_error)}")
            return False


def main():
    """Main function to run the Auto-GPR E2E test."""
    parser = argparse.ArgumentParser(
        description="Auto-GPR End-to-End Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python autogpr_e2e_test.py --config autogpr_config.yaml
  python autogpr_e2e_test.py --config autogpr_config.yaml --cleanup
  python autogpr_e2e_test.py --config autogpr_config.yaml --skip-workspace-creation
        """
    )
    
    parser.add_argument(
        "--config", 
        required=True, 
        help="Path to the auto-GPR configuration YAML file"
    )
    parser.add_argument(
        "--cleanup", 
        action="store_true", 
        help="Clean up created resources after test completion"
    )
    parser.add_argument(
        "--skip-workspace-creation", 
        action="store_true", 
        help="Skip workspace creation if it already exists"
    )
    
    args = parser.parse_args()
    
    try:
        # Create and run the test
        test = AutoGPRE2ETest(args.config)
        success = test.run_test(
            skip_workspace_creation=args.skip_workspace_creation,
            run_cleanup=args.cleanup
        )
        
        exit_code = 0 if success else 1
        exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n❌ Test failed with unexpected error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main() 