from setuptools import setup, find_packages
import os, re

with open(os.path.join("src", "grblogtools", "__init__.py")) as initfile:
    (version,) = re.findall('__version__ = "(.*)"', initfile.read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="grblogtools",
    version=version,
    author="Gurobi Optimization, LLC",
    description="Gurobi log file tools for parsing and data exploration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=["Windows", "Linux", "macOS"],
    url="https://github.com/Gurobi/grblogtools",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=["ipywidgets", "numpy", "pandas", "plotly", "xlsxwriter"],
    python_requires=">=3.6",
    include_package_data=True,
)
