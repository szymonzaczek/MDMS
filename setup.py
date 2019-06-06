import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mdms-szymonzaczek",
    version="0.99999994",
    author="Szymon Zaczek",
    author_email="szymon.zaczek@edu.p.lodz.pl",
    description='An interface to one of the most popular Molecular Dynamics codes - Amber - which aids user in '
                     'preparing and running their own simulations.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/szymonzaczek/MDMS",
    packages=setuptools.find_packages(),
    scripts=['mdms/mdms_menu.py'],
    install_requires=['numpy', 'pandas', 'biopython'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry"
    ])
