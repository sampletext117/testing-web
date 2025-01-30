from setuptools import setup, find_packages

setup(
    name="my_project",
    version="1.2",
    packages=find_packages(),
    install_requires=[
        "psycopg2",
        "pytest",
        "pytest-random-order"
    ]
)
