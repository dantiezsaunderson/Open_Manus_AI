from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="open_manus_ai",
    version="0.1.0",
    author="Open Manus AI Team",
    author_email="example@example.com",
    description="An open-source personal AI assistant with advanced capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dantiezsaunderson/Open_Manus_AI",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "open-manus=src.main:main",
        ],
    },
)
