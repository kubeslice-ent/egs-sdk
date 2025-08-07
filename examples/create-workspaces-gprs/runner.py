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
        print("Please set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=<value>")
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
            "CLUSTER_NAME": [os.getenv("EGS_CLUSTER_NAME")],
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
    
    try:
        # For user_script.py, don't capture output to allow interactive input
        if script == "user_script.py":
            result = subprocess.run(cmd, check=True)
        else:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Script completed successfully.")
            if result.stdout:
                print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script failed with exit code {e.returncode}")
        if script != "user_script.py" and e.stdout:
            print("Stdout:", e.stdout)
        if script != "user_script.py" and e.stderr:
            print("Stderr:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Script '{script}' not found. Make sure it exists in the current directory.")
        return False
    except Exception as e:
        print(f"Unexpected error running script: {e}")
        return False

def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(description="Manage workspaces and run scripts.")
    parser.add_argument("--teams", nargs="+", required=True, help="List of workspace teams")
    parser.add_argument("--kubeconfig", required=True, help="Path to the kubeconfig file")
    parser.add_argument("--admin", choices=["create", "delete"], help="Run admin script with create/delete action")
    parser.add_argument("--user", action="store_true", help="Run user script")
    
    args = parser.parse_args()
    
    # Check if kubeconfig file exists
    if not os.path.exists(args.kubeconfig):
        print(f"Error: Kubeconfig file '{args.kubeconfig}' not found.")
        sys.exit(1)
    
    # Check for required environment variables
    check_env_vars()

    # Generate the config file
    generate_config(args.teams, args.kubeconfig)
    
    # Run admin script if specified
    if args.admin:
        print(f"\n{'='*50}")
        print(f"Running admin script with action: {args.admin}")
        print(f"{'='*50}")
        
        success = run_script("admin_script.py", args.admin)
        
        if success and args.admin == "create":
            print("\nWaiting for 120 seconds for workspaces to be ready...")
            time.sleep(120)
        elif not success:
            print(f"\nAdmin script failed. Please check the errors above.")
            if args.admin == "create":
                print("Note: If workspaces already exist, this is expected behavior.")
                print("You can proceed with the user script if the workspaces are ready.")
            sys.exit(1)
    
    # Run user script if specified
    if args.user:
        print(f"\n{'='*50}")
        print("Running user script")
        print(f"{'='*50}")
        
        success = run_script("user_script.py")
        
        if not success:
            print(f"\nUser script failed. Please check the errors above.")
            sys.exit(1)
    
    print("\nAll operations completed successfully!")
    
if __name__ == "__main__":
    main()
