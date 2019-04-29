import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MDMS-szymonzaczek",
    version="0.1",
    author="Szymon Zaczek",
    author_email="szymon.zaczek@edu.p.lodz.pl",
    description=long_description,
    long_description='An interface to one of the most popular Molecular Dynamics codes - Amber - which aids user in '
                     'preparing and running their own simulations.',
    long_description_content_type="text/markdown",
    url="https://github.com/szymonzaczek/MDMS",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
)