"""Setup script for procedural design package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="procedural-design",
    version="0.1.0",
    description="Procedural generation tools for organic 3D structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/procedural-design",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "taichi>=1.7.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "trimesh>=3.9.0",
        "click>=8.0.0",
        "streamlit>=1.20.0",
        "scikit-image>=0.19.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "jupyter>=1.0.0",
            "notebook>=6.4.0",
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ]
    },
    entry_points={
        "console_scripts": [
            "procedural-design=cli.commands:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
