import json
import subprocess
import os
import time
import argparse

def generate_config(teams, kubeconfig):
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
            "CLUSTER_NAME": ["worker-1"],
            "SECRET_NAME": f"kubeslice-rbac-rw-slice-{team}",
            "USER_NAME": f"{team}-user",
            "USER_EMAIL": f"{team}-user@avesha.io",
        }
        configs[team].update(base_config)
    
    with open("config.json", "w") as file:
        json.dump(configs, file, indent=4)
    
    print("Config file 'config.json' has been generated successfully.")

def run_script(script, action=None):
    cmd = ["python", script, "config.json"]
    if action:
        cmd.append(action)
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Manage workspaces and run scripts.")
    parser.add_argument("--teams", nargs="+", required=True, help="List of workspace teams")
    parser.add_argument("--kubeconfig", required=True, help="Path to the kubeconfig file")
    parser.add_argument("--admin", choices=["create", "delete"], help="Run admin script with create/delete action")
    parser.add_argument("--user", action="store_true", help="Run user script")
    
    args = parser.parse_args()
    
    generate_config(args.teams, args.kubeconfig)
    
    if args.admin:
        run_script("admin_script.py", args.admin)
        if args.admin == "create":
            print("Waiting for 120 seconds ...")
            time.sleep(120)
    
    if args.user:
        run_script("user_script.py")
    
if __name__ == "__main__":
    main()
