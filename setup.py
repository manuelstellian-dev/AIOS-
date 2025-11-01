from setuptools import setup, find_packages

setup(
    name="aios-venom",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "cryptography>=41.0.0",
        "pyjwt>=2.8.0",
        "rich>=13.0.0",
        "psutil>=5.9.0",
        "networkx>=3.0",
        "transformers>=4.30.0",
        "torchvision>=0.15.0",
        "optuna>=3.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "Pillow>=10.0.0",
        "pandas>=1.5.0",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'venom-omega=venom.cli.omega_cli:main',
        ],
    },
)