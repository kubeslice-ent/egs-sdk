## Pre-Requisites

- Install EGS using the [EGS Installation Guide](https://docs.avesha.io/documentation/enterprise-egs/1.10.0/python-sdk/install-sdk#install-sdk)
- Run `pip install requests`
- 💻 Access to a Linux terminal connected to the internet
- 📦 `kubectl` installed
- ☁️ EGS installed on a Kubernetes cluster

## How to Run the Code

1. Expose `EGS_ENDPOINT` `EGS_API_KEY` `EGS_CLUSTER_NAME` as environment variables:

   - To get the `EGS_ENDPOINT`, run `kubectl get svc -n kubeslice-controller` and copy the `EXTERNAL-IP` of the `egs-core-apis` service and append `:8080` to it. Example: `http://<EXTERNAL-IP>:8080`
   - `EGS_API_KEY` can be obtained from the EGS UI
   - `EGS_CLUSTER_NAME` is the name of the cluster in your EGS account

### Manage Workspaces

1. Generate Config & Create Workspaces

```sh
python runner.py --teams team-beta team-gamma --kubeconfig /path/to/kubeconfig --admin create
```

2. Create GPRs

```sh
python runner.py --teams team-beta --kubeconfig /path/to/kubeconfig --user
```

3. Delete Workspaces

```sh
python runner.py --teams team-beta team-gamma --kubeconfig /path/to/kubeconfig --admin delete
```
