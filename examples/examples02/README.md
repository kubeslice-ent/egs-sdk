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

2. To create a workspace for a team, run the following command:

```sh
python runner.py --teams team-beta team-gamma --kubeconfig /path/to/<admin>-kubeconfig --admin create
```

- This will create a folder named `team-beta` and `team-gamma` in the current directory with the following files (for each team):
  - api-token.txt
  - `team-<team-name>-kubeconfig.yaml`
  - `team-<team-name>-token.txt`
- `team-<team-name>-kubeconfig.yaml` and `team-<team-name>-token.txt` are going to be populated by the script.
- User needs to log in to the EGS UI with the token from `team-<team-name>-token.txt` and create an `api-token` in the EGS UI.
- That api-token needs to be saved in api-token.txt

3. Once the api-token is saved in api-token.txt, run the following command to create GPRs for the team:

```sh
python runner.py --teams team-beta --kubeconfig /path/to/<team-name>-kubeconfig --user
```

4. To delete the workspaces, run the following command:

```sh
python runner.py --teams team-beta team-gamma --kubeconfig /path/to/<admin>-kubeconfig --admin delete
```
