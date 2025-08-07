#!/usr/bin/env python3
"""
Script to create RBAC secrets manually for EGS workspaces.
This script helps when the EGS system doesn't automatically create the required secrets.
"""

import subprocess
import json
import base64
import os
import sys

def create_rbac_secret(team_name, kubeconfig_file, namespace="kubeslice-avesha"):
    """Create a basic RBAC secret for the team."""
    secret_name = f"kubeslice-rbac-rw-slice-{team_name}"
    
    print(f"Creating RBAC secret '{secret_name}' for team '{team_name}'...")
    
    # Create a basic token (this is a placeholder - in production you'd get this from EGS)
    token_data = f"placeholder-token-for-{team_name}"
    token_encoded = base64.b64encode(token_data.encode()).decode()
    
    # Create the secret YAML
    secret_yaml = f"""apiVersion: v1
kind: Secret
metadata:
  name: {secret_name}
  namespace: {namespace}
type: Opaque
data:
  token: {token_encoded}
"""
    
    # Write to temporary file
    temp_file = f"temp_secret_{team_name}.yaml"
    with open(temp_file, "w") as f:
        f.write(secret_yaml)
    
    try:
        # Apply the secret
        result = subprocess.run(
            ["kubectl", "--kubeconfig", kubeconfig_file, "apply", "-f", temp_file],
            capture_output=True, text=True, check=True
        )
        print(f"✅ Secret '{secret_name}' created successfully")
        print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create secret '{secret_name}': {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def check_existing_secrets(team_name, kubeconfig_file, namespace="kubeslice-avesha"):
    """Check if secrets already exist for the team."""
    secret_name = f"kubeslice-rbac-rw-slice-{team_name}"
    
    try:
        result = subprocess.run(
            ["kubectl", "--kubeconfig", kubeconfig_file, "get", "secret", secret_name, "-n", namespace],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ Secret '{secret_name}' already exists")
            return True
        else:
            print(f"❌ Secret '{secret_name}' does not exist")
            return False
    except Exception as e:
        print(f"Error checking secret '{secret_name}': {e}")
        return False

def main():
    """Main function to create secrets for teams."""
    if len(sys.argv) < 3:
        print("Usage: python create_secrets_manually.py <team-name> <kubeconfig-file> [namespace]")
        print("Example: python create_secrets_manually.py team-beta /path/to/kubeconfig.yaml")
        sys.exit(1)
    
    team_name = sys.argv[1]
    kubeconfig_file = sys.argv[2]
    namespace = sys.argv[3] if len(sys.argv) > 3 else "kubeslice-avesha"
    
    print(f"🔧 Creating RBAC secrets for team '{team_name}'")
    print(f"📁 Using kubeconfig: {kubeconfig_file}")
    print(f"🏷️  Namespace: {namespace}")
    print("=" * 50)
    
    # Check if kubeconfig exists
    if not os.path.exists(kubeconfig_file):
        print(f"❌ Kubeconfig file not found: {kubeconfig_file}")
        sys.exit(1)
    
    # Check if secret already exists
    if check_existing_secrets(team_name, kubeconfig_file, namespace):
        print("Secret already exists. No action needed.")
        return
    
    # Create the secret
    if create_rbac_secret(team_name, kubeconfig_file, namespace):
        print(f"\n✅ Successfully created RBAC secret for team '{team_name}'")
        print("\n📝 Next steps:")
        print("1. The admin script should now be able to retrieve the secret")
        print("2. You may need to update the token with a real value from EGS")
        print("3. Run the admin script again to complete the setup")
    else:
        print(f"\n❌ Failed to create RBAC secret for team '{team_name}'")
        print("Please check your permissions and try again.")

if __name__ == "__main__":
    main() 