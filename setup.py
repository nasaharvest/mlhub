from setuptools import setup


setup(
    name="mlhub",
    description="Code to interact with mlhub.earth api",
    packages=["mlhub"],
    install_requires=[
        "boto3",
        "requests",
        "pandas",
        "numpy",
        "xarray",
        "rasterio",
        "netcdf",
    ],
)
