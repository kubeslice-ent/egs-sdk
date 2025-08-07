import egs
import subprocess
import time
import json
import requests
import os

def ask_to_continue(step):
    response = input(f"Do you want to continue to the next step: {step}? (yes/no): ")
    if response.lower() != "yes":
        print("Exiting script.")
        exit()


# Step 1: Authenticate with EGS using the user's API key
def authenticate(ENDPOINT, API_KEY):
    # ask_to_continue("Authenticate with EGS")
    print("Authenticating with EGS...")
    try:
        auth = egs.authenticate(endpoint=ENDPOINT, api_key=API_KEY)
        print("Authentication successful.")
        return auth
    except Exception as e:
        print(f"Authentication failed: {e}")
        raise

# Step 2: Create manual GPR requests for slices
def create_gpr_requests(auth, workspace_name, slices, CLUSTER_NAME):
    # ask_to_continue("Create GPR requests")
    for request_name, priority in slices.items():
        for i in range(1):
            print(f"Creating GPR request {request_name}_{i+1} for request '{request_name}' with priority '{priority}'...")

            try:
                inventory = egs.inventory(authenticated_session=auth).__str__()
                # convert string to json
                inventory = json.loads(inventory)
                print(f"Inventory retrieved successfully.")
                
                print(json.dumps(inventory, indent=4))

                if not inventory.get("managed_nodes") or len(inventory["managed_nodes"]) == 0:
                    print("No managed nodes found in inventory. Skipping GPR creation.")
                    continue

                print(inventory["managed_nodes"][0]["memory"], inventory["managed_nodes"][0]["instance_type"], inventory["managed_nodes"][0]["gpu_shape"])
                # print all the inventory items that are used in the GPR request
                print(inventory["managed_nodes"][0]["memory"], inventory["managed_nodes"][0]["instance_type"], inventory["managed_nodes"][0]["gpu_shape"])

                request_name = f"{request_name}_{i+1}"
                gpu_request_id = egs.request_gpu(
                    request_name=request_name, 
                    workspace_name=workspace_name, 
                    cluster_name=CLUSTER_NAME[0], 
                    node_count=1, 
                    gpu_per_node_count=1, 
                    memory_per_gpu=int(inventory["managed_nodes"][0]["memory"]), 
                    instance_type=inventory["managed_nodes"][0]["instance_type"], 
                    gpu_shape=inventory["managed_nodes"][0]["gpu_shape"], 
                    exit_duration="0d0h10m", 
                    priority=priority, 
                    authenticated_session=auth
                )

                print(f"GPR request {request_name}_{i+1} created successfully with GPU request ID '{gpu_request_id}'.")

                print(f"Waiting for 10 seconds before creating the next GPR request...")
                time.sleep(10)  # To avoid overwhelming the API
            except Exception as e:
                print(f"Error creating GPR request {request_name}_{i+1}: {e}")
                continue

# def delete_gpr_requests(auth, workspace_name):
#     # ask_to_continue("Delete GPR requests")
#     gpr_list = egs.gpu_request_status_for_workspace(workspace_name, authenticated_session=auth)
#     for gpr in gpr_list["items"]



def main():
    # take the config.json file as an argument
    import sys
    print(len(sys.argv))
    if len(sys.argv) != 2:
        print("Usage: python user_script.py <config.json>")
        exit(1)

    # get the config file
    config_file = sys.argv[1]

    # Load configuration from JSON file
    def load_config(file_path=config_file):
        with open(file_path, "r") as file:
            return json.load(file)

    # Load the configuration
    config_data = load_config()

    # Iterate over each team's configuration
    for team, config in config_data.items():
        print(f"\nProcessing configuration for team: {team}")

        # Extract values for the current team
        ENDPOINT = config["ENDPOINT"]
        WORKSPACE_NAME = config["WORKSPACE_NAME"]
        CLUSTER_NAME = config["CLUSTER_NAME"]

        # Read user api key from user folder
        api_token_file = f"./{team}/api-token.txt"
        if not os.path.exists(api_token_file):
            print(f"Warning: API token file '{api_token_file}' not found. Skipping team '{team}'.")
            print("Please ensure the admin script has been run and the API token has been added to the file.")
            continue

        try:
            with open(api_token_file, "r") as file:
                USER_API_KEY = file.read().strip()
            
            if not USER_API_KEY:
                print(f"Warning: API token file '{api_token_file}' is empty. Skipping team '{team}'.")
                print("Please add a valid API token to the file.")
                continue
        except Exception as e:
            print(f"Error reading API token file '{api_token_file}': {e}")
            continue

        # Placeholder for any further processing per team
        print(f"Completed processing API-Token for team: {team}\n{'='*50}")

        try:
            user_auth = authenticate(ENDPOINT=ENDPOINT, API_KEY=USER_API_KEY)
        except Exception as e:
            print(f"Failed to authenticate for team '{team}': {e}")
            continue

        # Define slices and their GPU shapes
        slices = {
            # "important fine tuning": 101,
            "EMERGENCY": 201
            # "critical simulation": 201
        }

        print("Installing GPU workloads...")

        # Check if kubeconfig file exists
        kubeconfig_file = f"./{team}/{team}-kubeconfig.yaml"
        if not os.path.exists(kubeconfig_file):
            print(f"Warning: Kubeconfig file '{kubeconfig_file}' not found. Skipping kubectl operations for team '{team}'.")
            continue

        try:
            subprocess.run(["kubectl", "--kubeconfig", kubeconfig_file, "--insecure-skip-tls-verify", "apply", "-f", f"./llm-deployment.yaml"], check=True)
            print("LLM deployment applied successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error applying LLM deployment: {e}")
            continue

        try:
            subprocess.run(["kubectl", "--kubeconfig", kubeconfig_file, "--insecure-skip-tls-verify", "apply", "-f", f"./service.yaml"], check=True)
            print("Service applied successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error applying service: {e}")
            continue

        # # sleep for 60 seconds
        # print("Waiting for 60 seconds ...")
        # time.sleep(60)

        print("Creating GPR requests...")
        # Create GPR requests for each slice
        create_gpr_requests(user_auth, WORKSPACE_NAME, slices, CLUSTER_NAME)
        
        print("GPU workload automation script completed successfully.")
        # delete_gpr_requests(user_auth, WORKSPACE_NAME)

        # Add sleep for 60 seconds to allow the service to be ready
        print("Waiting for 60 seconds for service to be ready...")
        time.sleep(60)

        # Create load against the service
        print("Preparing curl command to load the service...")

        try:
            command = [
                "kubectl", "--kubeconfig", kubeconfig_file,
                "--insecure-skip-tls-verify",
                "get", "svc", "llm-service",
                "-o", "jsonpath=\"{.status.loadBalancer.ingress[0].ip}\"",
                "-n", team
            ]
            print("Running command:", " ".join(command))

            external_ip = subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip().replace('"', '')

            if not external_ip:
                print("Warning: No external IP found for the service.")
            else:
                url = f"http://{external_ip}/generate"
                curl_cmd = f"""curl -X POST {url} \\
        -H "Content-Type: application/json" \\
        -d '{{"input": "What is Kubernetes?"}}'"""
                print("\nRun the following curl command to generate load:")
                print(curl_cmd)

        except subprocess.CalledProcessError as e:
            print(f"Error getting service external IP: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")



if __name__ == "__main__":
    main()
