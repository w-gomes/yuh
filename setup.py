from setuptools import setup, find_packages

setup(
    name = "yuh",
    version = "0.0.2",
    packages=find_packages(),
    py_modules=["yuh"],
    entry_points={
        'console_scripts': ['yuh=yuh:main']
    },
    python_requires = ">=3.12",
)
