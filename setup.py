from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='milvus_cli',
    version='0.1.7',
    author='Milvus Team',
    author_email='milvus-team@zilliz.com',
    url='https://github.com/milvus-io/milvus_cli',
    description='CLI for Milvus',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache-2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click==8.0.1',
        'pymilvus==2.0.0rc7',
        'tabulate==0.8.9'
    ],
    entry_points={
        'console_scripts': [
            'milvus_cli = milvus_cli.scripts.milvus_cli:runCliPrompt',
        ],
    },
    python_requires='>=3.8'
)
