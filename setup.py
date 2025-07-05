from setuptools import setup, find_packages

setup(
    name='quickcan',
    version='0.1.0',
    description='QuickCAN - USB to CAN Python interface',
    author='Alok Mishra',
    packages=find_packages(),
    install_requires=['pyserial', 'python-can'],
    entry_points={
        'console_scripts': [
            'quickcan-cli=cli.quickcan_cli:main',
        ],
        'can.interface': [
            'quickcan=backend.quickcan_bus:QuickCANBus',
        ],
    },
)
