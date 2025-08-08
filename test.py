import os

import egs
from egs.gpu_requests import request_gpu

# Global array of GPR request configurations
GPR_REQUESTS = [
    {
        "request_name": "test-gpr-auto-1",
        "workspace_name": "tezz-slice",
        "cluster_name": "",  # Empty for auto cluster selection
        "node_count": 1,
        "gpu_per_node_count": 1,
        "memory_per_gpu": 22,
        "exit_duration": "1h",
        "priority": 100,
        "idle_timeout_duration": "30m",
        "enforce_idle_timeout": True,
        "enable_auto_gpu_selection": True,  # Enable auto GPU selection
        "enable_auto_cluster_selection": True,  # Enable auto cluster selection
        "instance_type": "",  # Empty for auto GPU selection
        "gpu_shape": "",  # Empty for auto GPU selection
        # "preferred_clusters": ["worker-1", "worker-2"],  # Preferred clusters
        "description": "Auto selection GPR with high priority",
    },
    {
        "request_name": "test-gpr-cluster-auto-1",
        "workspace_name": "tezz-slice",
        "cluster_name": "",  # Empty for auto cluster selection
        "node_count": 1,
        "gpu_per_node_count": 1,
        "memory_per_gpu": 22,
        "exit_duration": "1h",
        "priority": 50,
        "idle_timeout_duration": "30m",
        "enforce_idle_timeout": True,
        "enable_auto_gpu_selection": False,  # Disable auto GPU selection
        "enable_auto_cluster_selection": True,  # Enable auto cluster selection
        "instance_type": "VM.GPU.A10.2",  # Specific instance type
        "gpu_shape": "NVIDIA-A10",  # Specific GPU shape
        # "preferred_clusters": ["worker-1", "worker-2"],  # Preferred clusters
        "description": "Auto cluster selection with manual GPU selection",
    },
    {
        "request_name": "test-gpr-manual-1",
        "workspace_name": "tezz-slice",
        "cluster_name": "worker-1",  # Specific cluster
        "node_count": 1,
        "gpu_per_node_count": 1,
        "memory_per_gpu": 22,
        "exit_duration": "1h",
        "priority": 25,
        "idle_timeout_duration": "30m",
        "enforce_idle_timeout": True,
        "enable_auto_gpu_selection": False,  # Disable auto GPU selection
        "enable_auto_cluster_selection": False,  # Disable auto cluster selection
        "instance_type": "VM.GPU.A10.2",  # Specific instance type
        "gpu_shape": "NVIDIA-A10",  # Specific GPU shape
        "preferred_clusters": ["worker-1", "worker-2"],  # Preferred clusters
        "description": "Manual cluster and GPU selection",
    }
]


def create_gpr(index=0):
    """
    Function to create a GPR with auto cluster selection and auto GPU selection enabled

    Args:
        index (int): Index of the GPR configuration to use from the global GPR_REQUESTS array
    """
    try:
        # Validate index
        if index < 0 or index >= len(GPR_REQUESTS):
            print(
                f"Error: Invalid index {index}. Available indices: 0 to {len(GPR_REQUESTS) - 1}"
            )
            return

        # Get endpoint and API key from environment variables or use defaults
        ENDPOINT = os.getenv("EGS_ENDPOINT", "http://143.47.115.243:8080")
        API_KEY = os.getenv("EGS_API_KEY", "15ca16e2-04ac-4758-a193-fbd2fb83a60a")

        # Check if credentials are properly set
        if ENDPOINT == "YOUR_ENDPOINT_HERE" or API_KEY == "YOUR_API_KEY_HERE":
            print("ERROR: Please set your EGS credentials!")
            print("You can either:")
            print("1. Set environment variables: EGS_ENDPOINT and EGS_API_KEY")
            print("2. Or edit this file and replace the placeholder values")
            print("3. Or create a config.json file with your credentials")
            return

        print("Authenticating with EGS...")
        auth = egs.authenticate(endpoint=ENDPOINT, api_key=API_KEY)
        print("Authentication successful.")

        # Get the request configuration from global array
        request_config = GPR_REQUESTS[index]
        print(f"Creating GPR: {request_config['description']}")
        print(f"Request name: {request_config['request_name']}")

        gpu_request_id = request_gpu(
            request_name=request_config["request_name"],
            workspace_name=request_config["workspace_name"],
            cluster_name=request_config["cluster_name"],
            node_count=request_config["node_count"],
            gpu_per_node_count=request_config["gpu_per_node_count"],
            memory_per_gpu=request_config["memory_per_gpu"],
            exit_duration=request_config["exit_duration"],
            priority=request_config["priority"],
            idle_timeout_duration=request_config["idle_timeout_duration"],
            enforce_idle_timeout=request_config["enforce_idle_timeout"],
            enable_auto_gpu_selection=request_config[
                "enable_auto_gpu_selection"
            ],
            enable_auto_cluster_selection=request_config[
                "enable_auto_cluster_selection"
            ],
            instance_type=request_config["instance_type"],
            gpu_shape=request_config["gpu_shape"],
            preferred_clusters=request_config["preferred_clusters"],
            authenticated_session=auth,
        )

        # Print the response
        print("Create GPR Response:")
        print("=" * 50)
        print(f"GPR Created Successfully with gpu_request_id: {gpu_request_id}")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    create_gpr(index=2)
