
# EGS SDK

The **Elastic GPU Service (EGS)** SDK provides tools and workflows for efficient GPU resource management across one or more Kubernetes clusters. It addresses critical gaps in LLM-Ops tools and schedulers by offering robust GPU scheduling, pre-configured GPU nodes and pools, and seamless resource management for cloud providers and users.

---

## Key Features 🚀

- **Efficient GPU Scheduling**: Manage GPU resources across multiple users and clusters seamlessly.
- **Pre-configured GPU Nodes and Pools**: Ready-to-use setups for fine-tuning jobs, enhancing GPU utilization and monetization.
- **Self-Service Portal**: Simplifies GPU resource management for a broader range of users.
- **Premium Service Delivery**: Enables cloud providers to offer white-glove services to larger customers.

---

## Installation 🛠️

To install the `egs-sdk` package, use the following command:

```bash
pip install git+https://github.com/kubeslice-ent/egs-sdk.git
```

If you wish to install a specific branch or version, specify it like this:

```bash
pip install git+https://github.com/kubeslice-ent/egs-sdk.git@<branch_or_tag_name>
```

Ensure you have Python 3.7 or higher installed on your system.

---

## Development 🧑‍💻

### Clone the Repository

To clone the repository and set up the development environment:

```bash
git clone https://github.com/kubeslice-ent/egs-sdk.git
cd egs-sdk
pip install -e .
```

### Run Tests

Tests are available to ensure the SDK works as expected. To run tests:

```bash
pytest
```

---
```markdown
---

## API Usage 📘

- [GPR Template Binding APIs](docs/gpr_template_binding.md)

---

## Contributing 🤝

We welcome contributions! Please open an issue or submit a pull request with your changes. Ensure you follow the project's coding standards and test your changes before submitting.

---

## Support 💬

For issues, feature requests, or questions, please visit the [GitHub Issues](https://github.com/kubeslice-ent/egs-sdk/issues) page.

---

## Resources 📚

- **Documentation**: [https://docs.avesha.io/documentation/enterprise-egs/0.8.0/overview/](https://docs.avesha.io/documentation/enterprise-egs/0.8.0/overview/)
- **Source Code**: [https://github.com/kubeslice-ent/egs-sdk](https://github.com/kubeslice-ent/egs-sdk)
- **Tracker**: [https://github.com/kubeslice-ent/egs-sdk/issues](https://github.com/kubeslice-ent/egs-sdk/issues)

---

For more detailed information, refer to the [Elastic GPU Service Overview](https://docs.avesha.io/documentation/enterprise-egs/0.8.0/overview/)

