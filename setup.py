from setuptools import setup, find_packages

setup(
    name="pymdbclient",
    version="1.0.0",
    description="Python package/CLI client for working with PyMDB",
    url="https://github.com/Py-MDB/PyMDB-Client",
    packages=find_packages(),
    package_data={"": ["ts_configs/*"]},
    install_requires=[
        "requests",
    ],
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pymdb=pymdbclient.__main__:main",
            "papi=pymdbclient.papi:main"
        ],
    },
)
