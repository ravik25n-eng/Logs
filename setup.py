from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="app-logs",
    version="0.1.0",
    author="Ravi K",
    author_email="ravik25n.eng@gmail.com",
    description="A logging package to insert application logs into PostgreSQL database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ravik25n-eng/Logs",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psycopg2-binary>=2.9.0",
    ],
)
