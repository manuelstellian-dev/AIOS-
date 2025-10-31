from setuptools import setup, find_packages

setup(
    name="aios-venom",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "cryptography>=41.0.0",
        "pyjwt>=2.8.0",
        "rich>=13.0.0",
    ],
    python_requires=">=3.8",
)