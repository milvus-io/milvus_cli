from setuptools import setup, find_packages

setup(
    name='milvus_cli',
    version='0.1.5',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'pymilvus==2.0.0rc5',
        'tabulate'
    ],
    entry_points={
        'console_scripts': [
            'milvus_cli = milvus_cli.scripts.milvus_cli:runCliPrompt',
        ],
    },
)
