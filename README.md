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
- biopython, numpy, pandas packages


### Installation

Use pip to install MDMS directly on your machine:

`pip install -i https://test.pypi.org/simple/ mdms-szymonzaczek`

In some cases, you might need to make mdms_menu.py file executable in order to use in any directory on your machine.

To do so, type following commands in the terminal:

`cd`

`cd .local/bin/`

`chmod +x mdms_menu.py`


### Installing dependencies

Use conda or pip to download required dependencies for running MDMS:

`conda install ambertools -c ambermd`

`pip install pandas`

`pip install numpy`

`pip install biopython`


### Getting Started

Change to the desired directory. All of the files will be stored there. Then simply type:

`mdms_menu.py`

Follow on-screen prompts to run your MD simulations!

If typing `mdms_menu.py` has no effect, you should make `mdms_menu.py` script an executable one. On how to do this, please refer to the Installation section.


### Features
- establishing initial protein (or protein-ligand complex) structure
  - downloading a protein structure directly from Protein Data Bank
  - using a protein structure that was earlier downloaded and/or somehow modified
  - checking if there are any missing atoms in amino acid residues (basing on the REMARK entries); this is also checked later on by pdb4amber
  - checking if there are any missing residues in the protein (basing on the REMARK entries)
  - automatic removal of residues, which are common leftovers after experiments
  - choosing which ligands are to be included for MD simulations
  - choosing if metal ions are to be retained for MD (if they are present in the crystal structure - user will must provide parameters for them though)
  - choosing if crystal waters are to be retained for MD (if they are present in the crystal structure - user will must add hydrogen atoms though)
  - reminding that user needs to add hydrogen atoms to ligands
  - reminding user that he should use functional oligomeric structure of the protein
- preparing topology and coordinate files for Amber
  - checking if there are hydrogen present in the ligand - if not, user is asked if this is on purpose
  - determining charges and force field parameters for ligands
  - processing chosen ligands and protein with pdb4amber
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
