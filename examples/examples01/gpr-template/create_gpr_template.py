import os
import egs
import argparse
import sys
import yaml

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
            if not config or "gpr_template" not in config:
                raise ValueError(
                    "Configuration file is empty or missing 'gpr_template' section."
                )
            return config
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration file: {str(e)}") from e
    

def validate_template_config(template_config):
    """
    Validate that an endpoint configuration has all required fields.
    """
    required_fields = [
        "name", "cluster_name", "gpu_shape", "instance_type",
        "memory_per_gpu", "number_of_gpus", "number_of_gpu_nodes", "exit_duration", "priority"
    ]

    missing_fields = [field for field in required_fields if field not in template_config]
    if missing_fields:
        raise ValueError(f"Missing required fields in template configuration: {missing_fields}")

    return True

def template_exists(templates, template_name):
    """
    Check if a template exists in the list of templates.
    """
    return any(template.name == template_name for template in templates)


    

if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
        description="Create GPR from YAML configuration"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file containing GPR Template Configurations"
    )

    args = parser.parse_args()

    # Create inference endpoints from YAML configuration
    try:
        # Load and validate YAML configuration
        config = load_yaml_config(args.config)

        # Authenticate with EGS
        auth = egs.authenticate(
            get_env_variable('EGS_ENDPOINT'),
            get_env_variable('EGS_API_KEY'),
            sdk_default=False
        )
        

        # Get list of workspaces for validation
        templates = egs.list_gpr_templates(authenticated_session=auth)


        for template_config in config.get("gpr_template", []):
            try:
                print(f"\n--- Processing template: {template_config.get('name', 'unnamed')} ---")


                validate_template_config(template_config)

            
                if template_exists(templates.items, template_config["name"]):
                    raise ValueError(f"Template '{template_config['name']}' already exists")

                # Get workspace inventory
                inventory = egs.workspace_inventory(
                    '*',
                    authenticated_session=auth
                )
                cur_inventory = inventory.workspace_inventory[0]


                # Extract parameters from config
                instance_type = template_config.get("instance_type")
                gpu_shape = template_config.get("gpu_shape")
                requested_memory_per_gpu = template_config.get("memory_per_gpu")
                requested_number_of_gpu_nodes = template_config.get("number_of_gpus")
                requested_number_of_gpus = template_config.get("number_of_gpu_nodes")

                matching_items = []

                # Match based on instance_type, optionally with gpu_shape
                if instance_type:
                    matching_items = [
                        item for item in inventory.workspace_inventory
                        if item.instance_type == instance_type and (not gpu_shape or item.gpu_shape == gpu_shape)
                    ]
                # Match only on gpu_shape if instance_type is not provided
                elif gpu_shape:
                    matching_items = [
                        item for item in inventory.workspace_inventory
                        if item.gpu_shape == gpu_shape
                    ]

                # Use matched inventory if found
                if matching_items:
                    cur_inventory = matching_items[0]
                elif instance_type or gpu_shape:
                    raise ValueError(
                        f"No matching inventory found for instance_type='{instance_type}'"
                        f"{' and gpu_shape=' + gpu_shape if gpu_shape else ''}"
                    )

                # Validate user-provided resource limits
                if requested_memory_per_gpu and requested_memory_per_gpu > cur_inventory.memory_per_gpu:
                    raise ValueError(
                        f"Requested memory_per_gpu ({requested_memory_per_gpu}) exceeds available "
                        f"({cur_inventory.memory_per_gpu})"
                    )

                if requested_number_of_gpu_nodes and requested_number_of_gpu_nodes > cur_inventory.gpu_per_node:
                    raise ValueError(
                        f"Requested number_of_gpu_nodes ({requested_number_of_gpu_nodes}) exceeds available "
                        f"({cur_inventory.gpu_per_node})"
                    )

                if requested_number_of_gpus and requested_number_of_gpus > cur_inventory.total_gpu_nodes:
                    raise ValueError(
                        f"Requested number_of_gpus ({requested_number_of_gpus}) exceeds available "
                        f"({cur_inventory.total_gpu_nodes})"
                    )

                print(f"Using inventory: {cur_inventory}")




                # Determine GPU specifications (use config values or inventory defaults)
                gpu_shape = template_config.get("gpu_shape") or cur_inventory.gpu_shape
                instance_type = template_config.get("instance_type") or cur_inventory.instance_type
                memory_per_gpu = template_config.get("memory_per_gpu") or cur_inventory.memory_per_gpu
                number_of_gpu_nodes = template_config.get("number_of_gpus") or getattr(cur_inventory, 'num_gpu_nodes', 1)
                number_of_gpus = template_config.get("number_of_gpu_nodes") or getattr(cur_inventory, 'gpu_per_node_count', 1)

                # Validate GPU specifications
                if not all([gpu_shape, instance_type, memory_per_gpu, number_of_gpu_nodes, number_of_gpus]):
                    raise ValueError("Missing required GPU specification. Provide GPU parameters in config or ensure inventory has these values.")

                # Create the GPR template
                gpr_template = egs.create_gpr_template(
                    name=template_config["name"],
                    cluster_name=template_config["cluster_name"],
                    gpu_per_node_count=number_of_gpus,
                    num_gpu_nodes=number_of_gpu_nodes,
                    memory_per_gpu=memory_per_gpu,
                    gpu_shape=gpu_shape,
                    instance_type=instance_type,
                    exit_duration=template_config["exit_duration"],
                    priority=template_config["priority"],
                    enforce_idle_timeout=template_config.get("enforce_idle_timeout", False),
                    enable_eviction=template_config.get("enable_eviction", False),
                    requeue_on_failure=template_config.get("requeue_on_failure", False),
                    authenticated_session=auth
                )

                print(f"✅ Template created successfully: {gpr_template}")

            except Exception as e:
                print(f"❌ Failed to create template '{template_config.get('name', 'unnamed')}': {e}")
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

