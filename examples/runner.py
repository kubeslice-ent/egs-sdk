import json
import subprocess
import os
import time
import argparse
import sys

# Required environment variables
REQUIRED_ENV_VARS = ["EGS_ENDPOINT", "EGS_API_KEY", "EGS_CLUSTER_NAME"]

def check_env_vars():
    """Check if all required environment variables are set."""
    missing_vars = [var for var in REQUIRED_ENV_VARS if os.getenv(var) is None]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

def generate_config(teams, kubeconfig):
    """Generate a configuration file for the given teams."""
    base_config = {
        "ENDPOINT": os.getenv("EGS_ENDPOINT"),
        "API_KEY": os.getenv("EGS_API_KEY"),
        "PROJECT_NAMESPACE": "kubeslice-avesha",
        "KUBECONFIG_FILE": kubeconfig
    }
    
    configs = {}
    for team in teams:
        configs[team] = {
            "WORKSPACE_NAME": team,
            "WORKSPACE_NAMESPACE": [team],
            "CLUSTER_NAME": os.getenv("EGS_CLUSTER_NAME"),
            "SECRET_NAME": f"kubeslice-rbac-rw-slice-{team}",
            "USER_NAME": f"{team}-user",
            "USER_EMAIL": f"{team}-user@avesha.io",
        }
        configs[team].update(base_config)
    
    with open("config.json", "w") as file:
        json.dump(configs, file, indent=4)
    
    print("Config file 'config.json' has been generated successfully.")

def run_script(script, action=None):
    """Run the specified script with the config file."""
    cmd = ["python", script, "config.json"]
    if action:
        cmd.append(action)
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(description="Manage workspaces and run scripts.")
    parser.add_argument("--teams", nargs="+", required=True, help="List of workspace teams")
    parser.add_argument("--kubeconfig", required=True, help="Path to the kubeconfig file")
    parser.add_argument("--admin", choices=["create", "delete"], help="Run admin script with create/delete action")
    parser.add_argument("--user", action="store_true", help="Run user script")
    
    args = parser.parse_args()
    
    # Check for required environment variables
    check_env_vars()

    # Generate the config file
    generate_config(args.teams, args.kubeconfig)
    
    # Run admin script if specified
    if args.admin:
        run_script("admin_script.py", args.admin)
        if args.admin == "create":
            print("Waiting for 120 seconds ...")
            time.sleep(120)
    
    # Run user script if specified
    if args.user:
        run_script("user_script.py")
    
if __name__ == "__main__":
    main()
