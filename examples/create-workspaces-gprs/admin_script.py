import egs
import subprocess
import time
import json
import base64
import os

def ask_to_continue(step):
    response = input(f"Do you want to continue to the next step: {step}? (yes/no): ")
    if response.lower() != "yes":
        print("Exiting script.")
        exit()

import json

# Step 1: Authenticate with EGS
def authenticate(ENDPOINT, API_KEY):
    # ask_to_continue("Authenticate with EGS")
    print("Authenticating with EGS...")
    auth = egs.authenticate(endpoint=ENDPOINT, api_key=API_KEY)
    print("Authentication successful.")
    return auth


# Step 2: Create workspace and associate it with the namespace
def create_workspace(auth, workspace_name, namespace, CLUSTER_NAME, USER_NAME, USER_EMAIL):
    # ask_to_continue("Create workspace ")
    print(f"Creating workspace '{workspace_name}' and associating it with namespace '{namespace}'...")
    try:
        workspace = egs.create_workspace(workspace_name, clusters=CLUSTER_NAME, namespaces=namespace, username=USER_NAME, email=USER_EMAIL, authenticated_session=auth)
        print(f"Workspace '{workspace_name}' created successfully.")
        return workspace
    except egs.exceptions.WorkspaceAlreadyExists:
        print(f"Workspace '{workspace_name}' already exists. Skipping creation.")
        return None
    except Exception as e:
        print(f"Error creating workspace '{workspace_name}': {e}")
        raise


def Delete_workspace(auth, workspace_name):
    # ask_to_continue("Deleting workspace {workspace_name}")
    print(f"Deleting workspace '{workspace_name}'")
    try:
        workspace = egs.delete_workspace(workspace_name, authenticated_session=auth)
        print(f"Workspace '{workspace_name}' deleted successfully.")
        return workspace
    except Exception as e:
        error_msg = str(e)
        if "active GPRs associated with the workspace" in error_msg:
            print(f"Workspace '{workspace_name}' has active GPRs.")
            print("Please manually delete GPRs first using kubectl or use the EGS UI to delete the workspace.")
            print("Example: kubectl delete gpr <gpr-name> -n kubeslice-avesha")
            raise e
        else:
            print(f"Error deleting workspace '{workspace_name}': {e}")
            raise

def get_secret_with_retry(kubeconfig_file, secret_name, namespace, max_retries=5, delay=5):
    """Get secret with retry logic to handle timing issues."""
    for attempt in range(max_retries):
        try:
            print(f"Attempting to get secret '{secret_name}' (attempt {attempt + 1}/{max_retries})...")
            secret = subprocess.run(
                ["kubectl", "--kubeconfig", kubeconfig_file, "get", "secrets", secret_name, "-n", namespace, "-o", "json"], 
                capture_output=True, text=True, check=True
            )
            secret_json = json.loads(secret.stdout)
            print(f"Secret '{secret_name}' retrieved successfully.")
            return secret_json
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:
                print(f"Secret '{secret_name}' not found yet. Waiting {delay} seconds before retry...")
                time.sleep(delay)
            else:
                print(f"Secret '{secret_name}' not found after {max_retries} attempts.")
                print("This might be normal if the EGS system doesn't automatically create RBAC secrets.")
                print("You may need to create the secret manually or use a different authentication method.")
                raise e

def main(): 
    # take the config.json file as an argument
    import sys
    if len(sys.argv) != 3:
        print("Usage: python admin_script.py <config.json> <create|delete>")
        exit(1)

    # Add another argument to accept either create or delete workspace
    operation = sys.argv[2]

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
        API_KEY = config["API_KEY"]
        WORKSPACE_NAME = config["WORKSPACE_NAME"]
        WORKSPACE_NAMESPACE = config["WORKSPACE_NAMESPACE"]
        CLUSTER_NAME = config["CLUSTER_NAME"]
        SECRET_NAME = config["SECRET_NAME"]
        USER_NAME = config["USER_NAME"]
        USER_EMAIL = config["USER_EMAIL"]
        PROJECT_NAMESPACE = config["PROJECT_NAMESPACE"]
        KUBECONFIG_FILE = config["KUBECONFIG_FILE"]

        # Placeholder for any further processing per team
        print(f"Completed processing for team: {team}\n{'='*50}")

        print("Starting GPU workload automation script...")

        # Admin Authentication with EGS    
        auth = authenticate(ENDPOINT,API_KEY)

        if operation == "create":
            # Admin Creates workspace
            print(f"Creating workspace for team: {team}")
            print(f"{WORKSPACE_NAME} {WORKSPACE_NAMESPACE} {CLUSTER_NAME} {USER_NAME} {USER_EMAIL}")
            workspace = create_workspace(auth, WORKSPACE_NAME, WORKSPACE_NAMESPACE, CLUSTER_NAME, USER_NAME, USER_EMAIL)
            
            # Only proceed if workspace was created or already exists
            if workspace is not None:
                print(f"Waiting for 10 seconds for workspace to be ready...")
                time.sleep(10)
            else:
                print(f"Workspace '{WORKSPACE_NAME}' already exists, proceeding with kubeconfig retrieval...")
            
            # ask_to_continue("Get kubeconfig")
            try:
                kubeconfig = egs.get_workspace_kubeconfig(workspace_name=WORKSPACE_NAME, cluster_name=CLUSTER_NAME[0], authenticated_session=auth)
                print("Kubeconfig retrieved successfully.")
                
                # saving kubeconfig to a file
                subprocess.run(["mkdir", "-p", f"./{team}"], check=True)
                with open(f"./{team}/{WORKSPACE_NAME}-kubeconfig.yaml", "w") as f:
                    f.write(kubeconfig)
            except Exception as e:
                print(f"Error retrieving kubeconfig for workspace '{WORKSPACE_NAME}': {e}")
                continue

            # Get secret with retry logic
            try:
                secret_json = get_secret_with_retry(KUBECONFIG_FILE, SECRET_NAME, PROJECT_NAMESPACE)
                token = secret_json['data']['token']
                token = base64.b64decode(token).decode('utf-8')
                
                # save the token to a file
                with open(f"./{team}/{WORKSPACE_NAME}-token.txt", "w") as f:
                    f.write(token)
                print(f"Token saved to ./{team}/{WORKSPACE_NAME}-token.txt")
            except Exception as e:
                print(f"Error retrieving secret '{SECRET_NAME}': {e}")
                print("Continuing without token file...")

            # Create an empty file called api-token.txt under the team folder
            try:
                subprocess.run(["touch", f"./{team}/api-token.txt"], check=True)
                print(f"Created api-token.txt placeholder in ./{team}/")
            except Exception as e:
                print(f"Error creating api-token.txt: {e}")

        elif operation == "delete":
            try:
                Delete_workspace(auth, WORKSPACE_NAME)
                # Clean up team directory if it exists
                team_dir = f"./{team}"
                if os.path.exists(team_dir):
                    subprocess.run(["rm", "-rf", team_dir], check=True)
                    print(f"Cleaned up team directory: {team_dir}")
            except Exception as e:
                print(f"Error during delete operation for team '{team}': {e}")


if __name__ == "__main__":
    main()
