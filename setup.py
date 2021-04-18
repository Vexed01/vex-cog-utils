from setuptools import setup

setup(
    name="vex-cog-utils",
    version="1.1.1",
    url="https://github.com/Vexed01/vex-cog-utils",
    author="Vexed01",
    author_email="gh.vexed@gmail.com",
    description="Utility functions for the Vex-Cogs repo.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["vexcogutils"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8.1",
)
