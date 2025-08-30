import os
import egs
import argparse
import sys
import yaml
import time

def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value

def load_yaml_config(config_path):
    """
    Load and validate YAML configuration file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            if not config or "template_bindings" not in config:
                raise ValueError(
                    "Configuration file is empty or missing 'template_bindings' section."
                )
            return config
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration file: {str(e)}") from e

def validate_binding_config(binding_config):
    """
    Validate that a binding configuration has all required fields.
    """
    # Check if workspace_name is required and present
    if "workspace_name" not in binding_config:
        raise ValueError("Missing required field: workspace_name")
    
    if not binding_config["workspace_name"]:
        raise ValueError("workspace_name cannot be empty")
    
    # If clusters is present, validate cluster structure
    if "clusters" in binding_config:
        if not isinstance(binding_config["clusters"], list):
            raise ValueError("clusters must be a list")
        
        if len(binding_config["clusters"]) == 0:
            raise ValueError("If clusters is specified, at least one cluster must be present")
        
        # Validate each cluster
        for i, cluster in enumerate(binding_config["clusters"]):
            if not isinstance(cluster, dict):
                raise ValueError(f"Cluster at index {i} must be a dictionary")
            
            if "cluster_name" not in cluster:
                raise ValueError(f"Missing required field 'cluster_name' in cluster at index {i}")
            
            if not cluster["cluster_name"]:
                raise ValueError(f"cluster_name cannot be empty in cluster at index {i}")
    
    return True

def template_exists(templates, template_name):
    """
    Check if a template exists in the list of templates.
    """
    return any(template.name == template_name for template in templates)


if __name__ == "__main__" :
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
        description="Update template binding from YAML configuration"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file containing inference endpoint specifications"
    )

    args = parser.parse_args()
    
    try:
        # Load and validate YAML configuration
        config = load_yaml_config(args.config)

        # Authenticate with EGS
        auth = egs.authenticate(
            get_env_variable('EGS_ENDPOINT'),
            get_env_variable('EGS_API_KEY'),
            sdk_default=False
        )
        for binding in config.get("template_bindings", []):
            try :
                print(f"\n--- Processing template binding: {binding.get('workspace_name', 'unnamed')} ---")
                validate_binding_config(binding)

                # Check if workspace exists
                workspaces = egs.list_workspaces(authenticated_session=auth)
                if not any(workspace.name == binding.get('workspace_name') for workspace in workspaces.workspaces):
                    raise ValueError(f"Workspace '{binding.get('workspace_name')}' does not exist")
                
                # Check if clusters exist in the workspace
                workspace_name = binding.get('workspace_name')
                workspace = next((w for w in workspaces.workspaces if w.name == workspace_name), None)
                
                # Get available clusters in the workspace
                available_clusters = workspace.clusters if hasattr(workspace, 'clusters') else []
                
                # Validate each cluster in the binding configuration
                if "clusters" in binding:
                    for cluster_config in binding["clusters"]:
                        cluster_name = cluster_config.get("cluster_name")
                        if cluster_name not in available_clusters:
                            raise ValueError(f"Cluster '{cluster_name}' not found in workspace '{workspace_name}'. Available clusters: {available_clusters}")
                
                # Check if templates exist
                templates = egs.list_gpr_templates(authenticated_session=auth)

                for cluster in binding["clusters"]:
                    # Check if default_template_name exists in the templates list
                    default_template = cluster.get("default_template_name")
                    if default_template and default_template not in cluster["templates"]:
                        raise ValueError(f"Default template '{default_template}' must be present in the templates list for cluster '{cluster['cluster_name']}'")
                    
                    # Check if all templates exist in the available templates
                    for template in cluster["templates"]:
                        if not template_exists(templates.items, template):
                            available_template_names = [template.name for template in templates.items]
                            print("Available templates:")
                            for name in available_template_names:
                                print(f"  - {name}")
                            raise ValueError(f"Template '{template}' does not exist. Available templates listed above.")
                        
                # CHECK IF BINDING ALREADY EXISTS
                workspace_name = binding.get("workspace_name")
                
                try:
                    # Try to get existing binding
                    existing_binding = egs.get_gpr_template_binding(
                        binding_name=workspace_name,
                        authenticated_session=auth
                    )
                    print(f"Found existing binding for workspace '{workspace_name}'")
                    
                except Exception as e:
                    print(f"No existing binding found for workspace '{workspace_name}', proceeding to update existing binding")
                
                transformed_clusters = []
                for cluster in binding["clusters"]:
                    transformed_cluster = {
                        "clusterName": cluster["cluster_name"],
                        "defaultTemplateName": cluster.get("default_template_name"),
                        "templates": cluster["templates"]
                    }
                    transformed_clusters.append(transformed_cluster)
                
                # update template binding
                enable_auto_gpr = binding.get("enable_auto_gpr", False)
                print(f"Updating template binding with enable_auto_gpr: {enable_auto_gpr}")
                
                response = egs.update_gpr_template_binding(
                    workspace_name=binding.get("workspace_name"),
                    clusters=transformed_clusters,
                    enable_auto_gpr=enable_auto_gpr,
                    authenticated_session=auth
                )
                
                print(f"✅ Successfully updated template binding for workspace '{binding.get('workspace_name')}'")
            
                
            except Exception as e:
                print(f"❌ Failed to update template binding '{binding.get('workspace_name', 'unnamed')}': {e}")
                continue    
        
    except FileNotFoundError as e:
        print(f"❌ Configuration file error: {e}")
        sys.exit(1)
    except EnvironmentError as e:
        print(f"❌ Environment error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)