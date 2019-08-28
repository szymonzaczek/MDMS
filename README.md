<p align="center">
    <img src="https://raw.githubusercontent.com/szymonzaczek/MDMS/linux_development/mdms_logo.png" alt="MDMS: Molecular Dynamics Made Simple">
</p>

# MDMS: Molecular Dynamics Made Simple

Perform Molecular Dynamics (MD) Simulations from scratch within minutes. This program is an interface to one of the most popular MD codes ([Amber](http://ambermd.org/)), aiding users in preparing and running their own simulations.

The idea behind MDMS design is that the beginnings should be easy - not exhausting. That is why this program accommodates everything that is required for getting realistic insights about protein/protein-ligand complexes through MD simulations.

Program's execution has four distinct steps:
- establishing protein/protein-ligand complex structure
- preparing topology and coordinate files for Amber
- preparing input files for Amber
- running MD simulations

MDMS is aimed both to newcomers to the field as well as mature scientists. Newcomers will mostly benefit from the ease of starting MD simulations and the guarantee that the systems are constructed correctly (if user will carefully follow on-screen prompts). Mature scientists should mostly appreciate time savings - with MDMS, MD simulations of the proteins might be initiated as quickly as in 2 minutes from the start of the program.


### Prerequisites

- Linux distribution with Bash shell
- Ambertools or Amber distribution
- pdb-tools, biopython, numpy, pandas packages

### Optional prerequisites

- Openbabel distribution along with Pybel package
- pdbfixer python package (part of Omnia software suite)
- Propka3.1 python package


### Installation

MDMS can be installed directly on your machine with either pip or conda.

Installing with pip:

`pip install mdms`

Installing with conda:

`conda install -c szymonzaczek mdms`


### Installing dependencies

Depending on which installation you will use, not all of the dependancies might have been installed.

For instance, neither installations automatically install Amber Tools - it is assumed that you already have it on your machine (this is due to the fact that there are a lot of ways to customly install Amber Tools).

If you do not have required dependancies installed yet (and they were not installed along with MDMS installation), use conda or pip to download them:

`conda install ambertools -c ambermd`

`pip install pdb-tools`

`pip install pandas`

`pip install numpy`

`pip install biopython`


### Optional dependancies

Following dependancies enable following functionalities:
- Open Babel is used for adding hydrogen atoms to ligands
- Propka is used to establish protonation states of residues within the structure
- Pdbfixer program is used for modelling missing residues in proteins

They might be installed by running following commands in the console:

`conda install -c openbabel openbabel`

`pip install PROPKA`

`conda install -c omnia pdbfixer `


### Getting Started

Change to the desired directory. All of the files will be stored there. Then simply type:

`mdms_menu`

Follow on-screen prompts to run your MD simulations!


### Features
- establishing initial protein (or protein-ligand complex) structure
  - downloading a protein structure directly from Protein Data Bank
  - using a protein structure that was earlier downloaded and/or somehow modified
  - choosing protein chains (if multiple chains are found in the structure)
  - checking if there are any missing atoms in amino acid residues 
  - checking if there are any missing residues in the protein
  - adding missing residues with pdbfixer
  - reminding user that he should use functional oligomeric structure of the protein
  - establishing protonation states of titrable residues using Propka3.1
  - general formatting of PDB files
  - optional removal of residues, which are common leftovers after experiments
  - choosing which ligands are to be included for MD simulations
  - adding hydrogen atoms to ligands
  - choosing if metal ions are to be retained for MD (if they are present in the crystal structure)
  - choosing if crystal waters are to be retained for MD (if they are present in the crystal structure
  - adding hydrogen atoms to crystal waters
- preparing topology and coordinate files for Amber
  - checking if there are hydrogen present in the ligand - if not, user is asked if this is on purpose
  - determining charges and force field parameters for ligands
  - processing chosen ligands and protein with pdb4amber
  - preparing input files for MCPB.py in order to obtain metal force field parameters
  - choosing protein force field
  - choosing water force field
  - choosing size of a solvation shell
  - creating topology and coordinate files
- preparing input files for Amber
  - choosing routine for simulations (full simulations - minimization, heating, equilibration and production or only a single step-simulation)
   - choosing QM/MM parameters
    - option to provide premade QM/MM namelist file
     - choosing basic QM/MM parameters (QM atoms, spin, charge, QM Hamiltonian)
     - changing current and/or adding custom parameters
  - choosing MD parameters
     - default MD parameters for each step are provided
     - changing values of current MD parameters and the ability to add custom ones (though they must work with Amber codes)
- running MD Simulations
  - choosing how simulations should be run - in queue or in terminal
    - if a queue was chosen, user must provide the appropriate script
  - choosing Amber code which will be run - Sander or PMEMD
  - choosing running mode - serial or parallel codes


### Contributing

If you are interested in contributing to MDMS, please either contact me at [szymon.zaczek@edu.p.lodz.pl](mailto:szymon.zaczek@edu.p.lodz.pl) or create pull request on Github.


### License

[MIT](https://github.com/szymonzaczek/MDMS/blob/master/LICENSE)


### Authors

* **Szymon Zaczek**
