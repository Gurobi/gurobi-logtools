from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="logextract",
    version="0.1.0",
    author = "Gurobi Optimization, LLC",
    description="Gurobi log file extractor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms = ["Windows", "Linux", "macOS"],
    url="https://github.com/Gurobi/logextract",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["ipywidgets", "numpy", "pandas", "plotly"],
    python_requires=">=3.6"
)