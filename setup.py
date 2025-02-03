from setuptools import setup, find_packages

setup(
    name="magento-config-tool",
    version="1.0.7",
    author="Yehor Shytikov",
    author_email="yegorshytikov@email.com",
    description="A terminal-based Magento configuration management tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/genaker/magento-config-tool",  # Update this
    packages=find_packages(),
    install_requires=[
        "tabulate",
        "sqlalchemy",
        "mysql-connector-python",
    ],
    entry_points={
        "console_scripts": [
            "mage-conf=magento_config_tool.magento_config_tool:run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Console",
    ],
    python_requires=">=3.6",
)
