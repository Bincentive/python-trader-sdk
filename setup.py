from setuptools import setup

setup(
    name='bincentive-trader',
    version='1.1.0',
    author='Bincentive',
    packages=['bincentive_trader'],
    install_requires=[
        'requests>=2.21',
        'pgpy>=0.4.3',
        'tzlocal>=1.5.1'
    ]
)
