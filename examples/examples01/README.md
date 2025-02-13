
# EGS SDK Examples
We provide an SDK example script to create workspaces. 

## Prerequisites

Before running the script, ensure the following requirements are met:

### Install the Required Python Package
```bash
pip install git+https://github.com/kubeslice-ent/egs-sdk.git
```
If you want to install a specific branch or version, specify the branch as in the following command:

```bash
pip install git+https://github.com/kubeslice-ent/egs-sdk.git@<branch_or_tag_name>
```

### KubeConfig Setup

The KubeConfig for the target cluster must be configured before running this script.

### Set Environment Variables

Ensure the following environment variables are set:

```bash
export EGS_ENDPOINT=<your-egs-endpoint>
export EGS_API_KEY=<your-egs-api-key>
```

### Python

Ensure you have Python version 3.9 or later installed on your system.

---

## Workspace Configuration YAML

The script uses a configuration file in YAML format. The following is an example YAML.

```bash
projectname: "avesha"
workspaces:
  - name: "workspace-b"
    namespaces:
      - "namespace-b2"
      - "namespace-b1"
    clusters:
      - "worker-1"
      # - "worker-2" (Optional additional cluster)
    username: "admin-1"
    email: "admin1@acme.io"
```

### YAML Parameters Description

* `projectname`: The project name associated with the workspaces.
* `workspaces`: A list of workspace configurations.
* `name`: The name of the workspace.
* `namespaces`: List of namespaces associated with the workspace.
* `clusters`: List of clusters to associate with the workspace.
* `username`: The username associated with the workspace.
* `email`: The contact email for the workspace.


## Running the Script

To create workspaces based on the configuration file, run:
```bash
python create_workspace.py --config workspace_config.yaml
```

## Script Capability 

* Authenticates with the EGS API using provided environment variables
* Reads the workspace configuration YAML file
* Creates workspaces based on the configuration
* Retrieves and saves the KubeConfig for each cluster under the corresponding workspace folder
* Fetches the authentication token from the Kubernetes secret and saves it as `token.txt` under the workspace folder

### Output

On a successful execution, the script will:

* Create workspaces and save kubeconfig files in `kubeconfigs/<workspace_name>/`
* Retrieve and save the Kubernetes authentication token as `token.txt`
* Log messages indicating success or failure for each step

## Troubleshooting

If you encounter issues, then:

* Ensure the kubeconfig for your cluster is correctly set up
* Verify that the correct EGS API credentials are being used
* Check for proper formatting of the YAML configuration file.
* Review error messages to identify missing dependencies or incorrect configurations
