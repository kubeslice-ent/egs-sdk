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
        "name"
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
    parser = argparse.ArgumentParser(
        description="Create GPR from YAML configuration"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file containing GPR Template Configurations"
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
        
        templates = egs.list_gpr_templates(authenticated_session=auth)

        for template_config in config.get("gpr_template", []):
            try:
                print(f"\n--- Processing template: {template_config.get('name', 'unnamed')} ---")

                validate_template_config(template_config)

                if not template_exists(templates.items, template_config["name"]):
                    raise ValueError(f"Template '{template_config['name']}' does not exist")
                
                egs.delete_gpr_template(template_config["name"], authenticated_session=auth)
                print(f"✅ Template deleted successfully: {template_config['name']}")
            except Exception as e:
                print(f"❌ Failed to delete template '{template_config.get('name', 'unnamed')}': {e}")
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