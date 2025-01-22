import egs
try:
    auth = egs.authenticate("http://34.73.243.79:8080", "ecf5bfc0-f25b-4a81-9e7f-70de5f5e5543", sdk_default=False)
    print(auth)
    workspace_name = "sdk"
    # egs.create_workspace("sdk", ["worker-1"], ["sdk"], "srini", "srini@avesha.io", auth)
    # print(str(egs.list_workspaces(authenticated_session=None)))
    # # print(egs.get_workspace_kubeconfig(workspace_name, authenticated_session=None))
    gpu_request_id = egs.request_gpu("richie", workspace_name, "worker-2", 1, 1, 40, "a2-highgpu-2g", "NVIDIA-A100-SXM4-40GB", "0d1h0m", 201, auth)
    print(gpu_request_id)
# # egs.cancel_gpu_request("gpr-e3484e75-ca9b", auth)
except Exception as e:
    print(e)