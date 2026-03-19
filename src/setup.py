"""
Kurulum scripti
"""

from pathlib import Path

from setuptools import setup, find_packages

PROJECT_ROOT = Path(__file__).resolve().parent.parent

with open(PROJECT_ROOT / "README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(PROJECT_ROOT / "requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="karbon-salinimi-agentic-ai",
    version="0.1.0",
    author="KarbonSalınımı Ekibi",
    description="CBAM belgelerinden otomatik veri çıkarımı yapan agentic AI sistemi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/KarbonSalınımProjesi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
)
