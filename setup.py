from pathlib import Path

from setuptools import setup

exc: dict = {}
with open(Path(__file__).parent / "vexcogutils" / "version.py") as fp:
    exec(fp.read(), exc)
version = exc["__version__"]


setup(
    name="vex-cog-utils",
    version=version,
    url="https://github.com/Vexed01/vex-cog-utils",
    author="Vexed01",
    author_email="gh.vexed@gmail.com",
    description="Utility functions for the Vex-Cogs repo.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["vexcogutils"],
    package_data={"vexcogutils": ["py.typed"]},
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8.1",
    install_requires=["tabulate"],
)
