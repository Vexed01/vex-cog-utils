from setuptools import setup

setup(
    name="Vex-Cog-Utils",
    url="https://github.com/Vexed01/vex-cog-utils",
    author="Vexed01"
    author_email="gh.vexed@gmail.com",
    description="Utility functions for the Vex-Cogs repo."
    long_description=open("README.md").read()
    long_description_content_type="text/markdown"
    packages=["cogutils"],
    install_requires=["Red-DiscordBot"],  # for some chat stuff
    version="0.0.0",
)
