from setuptools import setup, find_packages

setup(
    name="egs-sdk",
    version="1.1.0",  # Replace with the current version of your package
    description="Elastic GPU Service SDK for GPU resource management in Kubernetes clusters",
    long_description=(
        "The Elastic GPU Service platform offers a system and workflows for efficient GPU resource management "
        "across one or more Kubernetes clusters.\n\n"
        "The Elastic GPU Service (EGS) addresses a critical gap in the current landscape of LLM-Ops tools and schedulers. "
        "While most tools in the LLM ecosystem focus on managing the lifecycle of large language models, they often overlook "
        "the vital aspect of GPU scheduling and resource management across multiple users and clusters. Existing schedulers "
        "are similarly limited, primarily focusing on job scheduling within in-cluster GPU resources without addressing broader "
        "resource management across users and clusters.\n\n"
        "EGS meets this demand by providing pre-configured GPU nodes and pools, readily available for fine-tuning jobs, which "
        "improves GPU utilization and boosts monetization. Moreover, EGS enables cloud providers to deliver a premium, white-glove "
        "service to their larger customers. EGS also offers a self-service portal that simplifies and optimizes GPU resource management "
        "for a wider range of users."
    ),
    long_description_content_type="text/markdown",
    author="Smart Scaler",
    author_email="support@avesha.io",
    url="https://github.com/kubeslice-ent/egs-sdk.git",
    packages=find_packages(),
    install_requires=[
        # Add dependencies here, e.g., "requests>=2.25.1", "pandas>=1.3.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",  # Replace with your license type
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="EGS SDK Kubernetes GPU Resource Management Smart Scaler LLM-Ops",
    project_urls={
        "Documentation": "https://github.com/kubeslice-ent/egs-sdk#readme",
        "Source": "https://github.com/kubeslice-ent/egs-sdk.git",
        "Tracker": "https://github.com/kubeslice-ent/egs-sdk/issues",
    },
)
