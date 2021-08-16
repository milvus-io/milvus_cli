from setuptools import setup, find_packages

setup(
    name='milvus_cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'pymilvus-orm==2.0.0rc2',
        'tabulate'
    ],
    entry_points={
        'console_scripts': [
            'milvus_cli = milvus_cli.scripts.milvus_cli:runCliPrompt',
        ],
    },
)
