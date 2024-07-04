from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smart-autonomous-assistants",
    version="0.1.2",
    author="jeblister",
    author_email="jeblister@waveup.dev",
    description="A system for orchestrating multiple AI assistants to accomplish complex tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/waveuphq/smart-autonomous-assistants",
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "phidata==2.4.22",
        "pydantic==2.7.4",
        "python-dotenv==1.0.1",
        "typer==0.12.3",
        "rich==13.7.1",
    ],
    entry_points={
        "console_scripts": [
            "smart-assistants=src.main:app",
        ],
    },
)
