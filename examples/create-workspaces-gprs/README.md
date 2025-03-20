# 🚀 EGS Workspace Automation Guide

🔹 Managing teams in EGS just got easier! This script automates the process of:

✅ Creating workspaces for different teams 🏢

✅ Generating team-specific credentials 🔑

✅ Setting up GPRs (Global Policy Rules) for users 👥

✅ Deleting workspaces when they're no longer needed 🗑️

🔹 With just a few commands, you can streamline access control and policy management in your EGS-powered Kubernetes cluster! 🎯

## 📌 Pre-Requisites

🔹 Before you jump in, make sure you have the following:

✔️ EGS installed on a Kubernetes cluster (Follow the EGS Installation Guide)

✔️ pip install requests (Make sure this Python package is installed)

✔️ 💻 Access to a Linux terminal connected to the internet

✔️ 📦 kubectl installed and configured

## 🚀 Running the Script

1️⃣ Set Up Your Environment
Export the following environment variables before running the script:

```
export EGS_ENDPOINT=http://<EXTERNAL-IP>:8080
export EGS_API_KEY=<YOUR_API_KEY>
export EGS_CLUSTER_NAME=<YOUR_CLUSTER_NAME>
```

👉 Get the EGS_ENDPOINT by running:

```
kubectl get svc -n kubeslice-controller
Copy the EXTERNAL-IP of the egs-core-apis service and append :8080 to it.
```

👉 Find EGS_API_KEY in the EGS UI.

👉 Use EGS_CLUSTER_NAME as it appears in your EGS account.

## 2️⃣ Create a Workspace for a Team

Run the following command to create workspaces for teams:

```
python runner.py --teams team-beta team-gamma --kubeconfig /path/to/<admin>-kubeconfig --admin create
```

🔹 This will generate directories for each team (team-beta, team-gamma) with:
📜 api-token.txt – Placeholder for the EGS API token
📜 team-<team-name>-kubeconfig.yaml – Kubernetes config for the team
📜 team-<team-name>-token.txt – Temporary login token for EGS UI

🔹 Next Step: Log in to the EGS UI with the token from team-<team-name>-token.txt and generate an API token.
🔹 Save that API token in api-token.txt inside the respective team’s directory.

## 3️⃣ Create GPRs for the Team

Onc
e the api-token.txt is updated, run:

```
python runner.py --teams team-beta --kubeconfig /path/to/<team-name>-kubeconfig --user
```

🔹 This configures Global Policy Rules (GPRs) for the team, granting them necessary permissions.

## 4️⃣ Delete Workspaces

If a workspace is no longer needed, delete it with:

```
python runner.py --teams team-beta team-gamma --kubeconfig /path/to/<admin>-kubeconfig --admin delete
```

🗑️ This removes all resources associated with the specified teams.

💡 And that’s it! In just a few simple steps, you can efficiently manage EGS workspaces, ensuring smooth operations in your Kubernetes cluster. 🚀
