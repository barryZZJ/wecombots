from setuptools import setup, find_packages

setup(
    name='crontab_manager',
    version='0.1',
    author='Barry ZZJ',
    description='register python file to crontab',
    packages=find_packages(),
    install_requires=[
        # list any dependencies your package requires
        'argparse',
        'python-crontab'
    ],
)
