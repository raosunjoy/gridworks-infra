"""
GridWorks B2B Infrastructure Services Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gridworks-b2b-sdk",
    version="1.0.0",
    author="GridWorks Infrastructure Services",
    author_email="sdk@gridworks.com",
    description="GridWorks B2B Infrastructure Services SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raosunjoy/gridworks-infra",
    project_urls={
        "Bug Tracker": "https://github.com/raosunjoy/gridworks-infra/issues",
        "Documentation": "https://docs.gridworks.com/sdk/python",
        "Source": "https://github.com/raosunjoy/gridworks-infra/tree/master/shared-infrastructure/sdks/python"
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0",
        "websockets>=11.0.0",
        "cryptography>=41.0.0",
        "PyJWT>=2.8.0",
        "python-dateutil>=2.8.0",
        "typing-extensions>=4.5.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "tenacity>=8.2.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.24.0",
            "respx>=0.20.0",
        ]
    },
    keywords=[
        "gridworks",
        "b2b",
        "financial-services",
        "trading",
        "banking",
        "ai-suite",
        "anonymous-services",
        "sdk",
        "python",
        "fintech",
        "infrastructure"
    ],
    include_package_data=True,
    zip_safe=False,
)