import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")

# Configuration
TEMPLATE_NAME = "vllm-template"


def delete_workload_template():
    """Example: Delete a workload template."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    # Confirm deletion
    print(f"About to delete workload template: {TEMPLATE_NAME}")
    confirm = input("Are you sure? (yes/no): ")

    if confirm.lower() != "yes":
        print("Deletion cancelled.")
        sys.exit(0)

    try:
        response = egs.workloadTemplate.delete(
            name=TEMPLATE_NAME,
            authenticated_session=auth,
        )
    except Exception as e:
        print(f"Error deleting workload template: {e}")
        sys.exit(1)

    print(f"Deleted workload template: {response.name}")


if __name__ == "__main__":
    delete_workload_template()
