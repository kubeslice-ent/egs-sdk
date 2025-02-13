
import egs
from egs.internal.gpr.gpr_status_data import GpuRequestStatus
import argparse
import logging
import os
import sys


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


# Example usage
if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
                    description="Make GPR Options")

    parser.add_argument("--request_id",
                        required=True,
                        help='The unique GPU request ID')

    args = parser.parse_args()

    try:
        auth = egs.authenticate(get_env_variable('EGS_ENDPOINT'),
                                get_env_variable('EGS_API_KEY'),
                                sdk_default=False)

        gpu_request = egs.gpu_request_status(args.request_id, auth)
        print(f'Current GPR Provisioning status :{gpu_request.status.provisioning_status}')

        if (gpu_request.status.provisioning_status == "Queued" or gpu_request.status.provisioning_status == "Pending"):
            print('Hence Canceling GPU Request')
            egs.cancel_gpu_request(request_id=args.request_id,
                                   authenticated_session=auth)
        elif gpu_request.status.provisioning_status == "Complete":
            print('GPR is already Completed')
        else:
            print('Hence Releasing GPU Request')
            egs.release_gpu(request_id=args.request_id,
                            authenticated_session=auth)

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)
