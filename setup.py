"""
ByteCityBD - Setup configuration for ERPNext custom app
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="bytecitybd",
    version="0.0.1",
    description="ERPNext Custom App for Flutter Web/Mobile Integration",
    author="ByteCityBD",
    author_email="info@bytecitybd.com",
    url="https://github.com/bytecitybd/bytecitybd",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)