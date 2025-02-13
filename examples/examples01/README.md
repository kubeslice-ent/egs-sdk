
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

## Workspace

### Workspace Configuration YAML

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


### Running the Script

To create workspaces based on the configuration file, run:
```bash
python create_workspace.py --config workspace_config.yaml
```

## GPR

### Create a GPR
The make-gpr.py script is used to create a GPR.

Syntax
```bash
python make_gpr.py --cluster_name <cluster-name> --workspace_name <workspace-name> --priority <priority-number> --exit_duration <duration-in-minutes> --request_name <gpr-request-name> --gpu_shape <GPU shape>
```


Examples
note
The --gpu_shape shape is an optional parameter. If the provided GPU shape is not found or if the --gpu_shape parameter is not passed. It will default to first node, first GPU.

The following is an example command to create a GPR (passing gpu-shape parameter):
```bash
python make_gpr.py --cluster_name "worker-1" --workspace_name test1 --priority 100 --exit_duration 5m --request_name test-gpr4 --gpu_shape Tesla-P100-PCIE-16GB
```

Example Output
```bash
Workspace test1 exists in worker-1 cluster
Tesla-P100-PCIE-16GB
{"cluster_name": "worker-1", "gpu_per_node": 2, "gpu_shape": "Tesla-P100-PCIE-16GB", "instance_type": "n1-highcpu-2", "memory_per_gpu": 16, "total_gpu_nodes": 1}
GPR Created Successfully with gpu_request_id:  gpr-7bdeec73-06be
```

The following is an example command to create a GPR (without gpu-shape parameter):
```bash
python make_gpr.py --cluster_name "worker-1" --workspace_name test1 --priority 100 --exit_duration 5m --request_name test-gpr1
```

Example Output
```bash
Workspace test1 exists in worker-1 cluster
GPR Created Successfully with gpu_request_id:  gpr-4d8e77d1-632d
```

Release a GPR
The release_gpr.py script is used to release a GPR. The GPR request ID is provided as input parameter to the script.

Syntax
```bash
python release_gpr.py --request_id <gpr-request-id>
```

Example
The following is an example command to release a GPR:
```bash
python release_gpr.py --request_id gpr-191b3dd5-f110
```

Example Output (If the GPR request is in queue)
```bash
Current GPR Provisioning status :Queued
Hence Canceling GPU Request
```

Example Output (If the GPR is provisioned)

```bash
Current GPR Provisioning status :Successful
Hence Releasing GPU Request
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
