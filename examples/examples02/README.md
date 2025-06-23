# EGS SDK Auto-GPR Examples for Manual Testing

This directory contains examples for testing Auto-GPR functionality with the **"purple"** workspace. Auto-GPR enables automatic creation of GPU Provisioning Requests (GPRs) based on workload demands without manual intervention.

## Overview

Auto-GPR introduces two key components:

- **GPR Templates**: Predefined configurations for creating GPRs with minimal user input
- **GPR Template Bindings**: Associations between templates and workspaces (slices) with auto-GPR enablement

## Prerequisites

### Install Required Python Packages

```bash
pip install git+https://github.com/kubeslice-ent/egs-sdk.git
pip install kubernetes pyyaml
```

### Environment Variables

The environment variables are pre-configured in the setup scripts:

**PowerShell:**

```powershell
.\set_env_vars.ps1
```

**Command Prompt:**

```cmd
set_env_vars.bat
```

**Manual setup:**

```bash
export EGS_ENDPOINT=http://35.229.87.139:8080
export EGS_API_KEY=0afc6c1e-30a4-4058-a0de-23e3c75d9933
```

## Manual Testing Steps

### 1. Setup Environment

```bash
# Windows PowerShell
.\set_env_vars.ps1

# Windows Command Prompt
set_env_vars.bat

# Linux/macOS
export EGS_ENDPOINT=http://35.229.87.139:8080
export EGS_API_KEY=0afc6c1e-30a4-4058-a0de-23e3c75d9933
```

### 2. Test GPR Template Management

**Create templates based on cluster inventory:**

```bash
python manage_gpr_templates.py --action create --config template_config.yaml
```

**List created templates:**

```bash
python manage_gpr_templates.py --action list
```

**Get specific template details:**

```bash
python manage_gpr_templates.py --action get --template-name purple-high-performance-template
```

### 3. Test GPR Template Binding

**Create binding to enable auto-GPR:**

```bash
python manage_gpr_bindings.py --action create --config binding_config.yaml
```

**List bindings:**

```bash
python manage_gpr_bindings.py --action list
```

**Get binding details:**

```bash
python manage_gpr_bindings.py --action get --binding-name purple
```

### 4. Run End-to-End Auto-GPR Test

**Complete auto-GPR setup:**

```bash
python autogpr_e2e_test.py --config autogpr_config.yaml
```

**With cleanup:**

```bash
python autogpr_e2e_test.py --config autogpr_config.yaml --cleanup
```

### 5. Test Auto-GPR with Sample Workloads

After setting up templates and bindings, deploy sample workloads to test auto-GPR:

```bash
# Deploy sample workloads (these will trigger auto-GPR)
kubectl apply -f sample_workloads.yaml

# Check if GPRs were created automatically
python ../../examples01/release_gpr.py --request_id <gpr-id>
```

## Configuration Files

### Main Configuration (`autogpr_config.yaml`)

- Configured for workspace **"purple"**
- Uses cluster **"worker-1"**
- Creates two template types: high-performance and standard

### Template Configuration (`template_config.yaml`)

- **purple-high-performance-template**: For priority workloads (1h duration, 30m idle timeout)
- **purple-standard-template**: For general workloads (30m duration, 15m idle timeout)
- Both use **NVIDIA-A100-80GB** GPUs based on your cluster inventory

### Binding Configuration (`binding_config.yaml`)

- Binds templates to workspace **"purple"**
- Enables auto-GPR functionality
- Sets **purple-high-performance-template** as default

## Auto-GPR Workflow

### Manual GPR (Traditional)

1. User creates GPR manually through UI/API
2. User specifies all parameters (GPU count, shape, priority, etc.)
3. GPR goes through provisioning
4. User deploys workload after GPR is ready

### Auto-GPR (Automated)

1. **Admin Setup**: Create templates and bindings (using scripts above)
2. **User Deployment**: Deploy workload with GPU requests in **purple** namespace
3. **Automatic Processing**:
   - AIOps webhook adds scheduling gate to workload
   - EGS agent detects GPU request and creates GPR using template
   - GPR gets provisioned automatically
   - AIOps operator removes scheduling gate when ready
   - Workload gets scheduled on GPU nodes

## Sample Workloads

The `sample_workloads.yaml` contains examples:

- **ml-training-pod**: Simple GPU pod for training
- **distributed-training**: Deployment with multiple replicas
- **batch-processing-job**: Batch job example

All workloads are configured for the **purple** namespace and single GPU requests.

## Verification

### Check GPR Status

```bash
# List all GPRs to see auto-created ones
# (Use existing EGS tools or API calls)
```

### Monitor Workloads

```bash
# Check workload status
kubectl get pods -n purple

# Check for scheduling gates
kubectl describe pod <pod-name> -n purple
```

## Troubleshooting

### Common Issues

1. **Template Creation Fails**

   - Verify workspace "purple" exists
   - Check cluster inventory availability
   - Ensure API key has proper permissions

2. **Binding Creation Fails**

   - Verify templates exist before creating binding
   - Check workspace name matches exactly

3. **Auto-GPR Not Triggered**
   - Ensure binding has `enableAutoGpr: true`
   - Check workload has GPU requests in resource limits
   - Verify workload is in **purple** namespace

### Debug Commands

```bash
# Check template status
python manage_gpr_templates.py --action list --format json

# Check binding status
python manage_gpr_bindings.py --action get --binding-name purple --format yaml

# Validate environment
echo $EGS_ENDPOINT
echo $EGS_API_KEY
```

## Cleanup

### Delete Resources

```bash
# Delete binding
python manage_gpr_bindings.py --action delete --binding-name purple

# Delete templates
python manage_gpr_templates.py --action delete --template-name purple-high-performance-template
python manage_gpr_templates.py --action delete --template-name purple-standard-template

# Delete workloads
kubectl delete -f sample_workloads.yaml
```

## Next Steps

1. **Create Templates**: Run template creation to match your cluster inventory
2. **Enable Auto-GPR**: Create binding to enable auto-GPR for purple workspace
3. **Test Workloads**: Deploy sample workloads and verify auto-GPR triggers
4. **Monitor Results**: Check GPR creation and workload scheduling
5. **Iterate**: Adjust template parameters based on test results
