# 🚀 EGS Workspace Automation Guide

🔹 Managing teams in EGS just got easier! This script automates the process of:

✅ Creating workspaces for different teams 🏢

✅ Generating team-specific credentials 🔑

✅ Setting up GPRs (GPU Requests) for users 👥

✅ Deleting workspaces when they're no longer needed 🗑️

## 📌 Pre-Requisites

🔹 Before you jump in, make sure you have the following:

✔️ EGS installed on a Kubernetes cluster (Follow the EGS Installation Guide)

✔️ pip install requests (Make sure this Python package is installed)

✔️ 💻 Access to a Linux terminal connected to the internet

✔️ 📦 kubectl installed and configured

✔️ 🐍 Python environment with EGS SDK installed (conda environment recommended)

## 🚀 Running the Script

### 1️⃣ Set Up Your Environment

**Activate the conda environment with EGS SDK:**

```bash
conda activate avesha
```

**Export the following environment variables:**

```bash
export EGS_ENDPOINT=http://<EXTERNAL-IP>:8080
export EGS_API_KEY=<YOUR_API_KEY>
export EGS_CLUSTER_NAME=<YOUR_CLUSTER_NAME>
```

👉 Get the EGS_ENDPOINT by running:

```bash
kubectl get svc -n kubeslice-controller
# Copy the EXTERNAL-IP of the egs-core-apis service and append :8080 to it.
```

👉 Find EGS_API_KEY in the EGS UI.

👉 Use EGS_CLUSTER_NAME as it appears in your EGS account.

### 2️⃣ Create a Workspace for a Team

Run the following command to create workspaces for teams:

```
python runner.py --teams team-beta team-gamma --kubeconfig /path/to/<admin>-kubeconfig --admin create
```

🔹 This will generate directories for each team (team-beta, team-gamma) with:

📜 api-token.txt – Placeholder for the EGS API token

📜 team-\<team-name\>-kubeconfig.yaml – Kubernetes config for the team

📜 team-\<team-name\>-token.txt – Temporary login token for EGS UI

🔹 Next Step: Log in to the EGS UI with the token from team-<team-name>-token.txt and generate an API token.

🔹 Save that API token in api-token.txt inside the respective team's directory.

### 3️⃣ Create GPRs for the Team

Once the api-token.txt is updated, run:

```
python runner.py --teams team-beta --kubeconfig /path/to/<team-name>-kubeconfig --user
```

🔹 This configures Global Policy Rules (GPRs) for the team, granting them necessary permissions.

### 4️⃣ Delete Workspaces

If a workspace is no longer needed, delete it with:

```
python runner.py --teams team-beta team-gamma --kubeconfig /path/to/<admin>-kubeconfig --admin delete
```

🗑️ This removes all resources associated with the specified teams.

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Workspace Already Exists Error

```
egs.exceptions.WorkspaceAlreadyExists: {"exception": {"data": null, "error": {"data": "Error: sliceconfigs.controller.kubeslice.io \"team-beta\" already exists...
```

**Solution**: This is now handled gracefully by the updated script. The script will:

- Detect existing workspaces
- Skip creation and continue with other operations
- Proceed to retrieve kubeconfig and tokens

#### 2. Secret Not Found Error

```
subprocess.CalledProcessError: Command '['kubectl', '--kubeconfig', '...', 'get', 'secrets', 'kubeslice-rbac-rw-slice-team-beta', '-n', 'kubeslice-avesha', '-o', 'json']' returned non-zero exit status 1
```

**Solution**: The updated script includes retry logic that:

- Waits for secrets to be created (up to 25 seconds)
- Retries the secret retrieval operation
- Continues gracefully if secrets are not available

#### 3. Missing Environment Variables

```
Error: Missing required environment variables: EGS_ENDPOINT, EGS_API_KEY, EGS_CLUSTER_NAME
```

**Solution**: Ensure all required environment variables are set:

```bash
export EGS_ENDPOINT=http://<your-egs-endpoint>:8080
export EGS_API_KEY=<your-api-key>
export EGS_CLUSTER_NAME=<your-cluster-name>
```

#### 4. Kubeconfig File Not Found

```
Error: Kubeconfig file '/path/to/kubeconfig' not found.
```

**Solution**: Verify the kubeconfig file path is correct and the file exists.

#### 5. API Token File Missing or Empty

```
Warning: API token file './team-beta/api-token.txt' not found. Skipping team 'team-beta'.
```

**Solution**:

1. Run the admin script first to create the team directory
2. Add a valid API token to the `api-token.txt` file in the team directory

#### 6. EGS Module Not Found

```
ModuleNotFoundError: No module named 'egs'
```

**Solution**: Activate the conda environment that has the EGS SDK installed:

```bash
conda activate avesha
```

### Testing the Scripts

Run the test script to verify basic functionality:

```bash
python3 test_runner.py
```

This will test:

- Config file generation
- Environment variable checking
- File existence validation

### Debug Mode

For detailed debugging, you can run individual scripts directly:

```bash
# Test admin script
python admin_script.py config.json create

# Test user script
python user_script.py config.json
```

## 📋 Script Improvements

The scripts now include:

✅ **Robust Error Handling**: Graceful handling of common errors and edge cases

✅ **Retry Logic**: Automatic retries for operations that may take time (like secret creation)

✅ **Better Logging**: More informative output and error messages

✅ **File Validation**: Checks for required files before operations

✅ **Graceful Degradation**: Continues processing other teams if one fails

✅ **Cleanup Operations**: Automatic cleanup of team directories during deletion

## 🎯 Best Practices

1. **Always activate the conda environment** before running scripts
2. **Always run admin script first** before user script
3. **Verify environment variables** are set correctly
4. **Check kubeconfig file paths** are valid
5. **Monitor script output** for any warnings or errors
6. **Use test script** to validate setup before running main operations
7. **Use the correct kubeconfig file** that has access to the required namespaces

💡 And that's it! In just a few simple steps, you can efficiently manage EGS workspaces, ensuring smooth operations in your Kubernetes cluster. 🚀
