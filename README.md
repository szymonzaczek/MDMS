<div align="center">
  <img src="https://raw.githubusercontent.com/szymonzaczek/MDMS/linux_development/mdms_logo.png"><br>
</div>

# MDMS: Molecular Dynamics Made Simple

Perform Molecular Dynamics (MD) Simulations from scratch within minutes. This program is an interface to one of the most popular MD codes - [Amber](http://ambermd.org/) - aiding users in preparing and running their own simulations.
Provided (or downloaded from Protein Data Bank using MDMS) PDB structure is at first checked for anomalies (missing atoms, missing residues). Then, user chooses which ligands will be included in the system for MD simulations.
The next steps include determining custom force field parameters for ligands, solvating the system, creating topology and initial coordinates files. Finally, user specifies options that will control MD and at long last, simulations might be started.


### Prerequisites

- Linux distribution with Bash shell
- Ambertools, biopython, numpy, pandas packages


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

Change to the directory in which you will want to store all of your files. Then simply type:
`mdms_menu.py`

Follow on-screen prompts to run your MD simulations!

If typing `mdms_menu.py` has no effect, you should make `mdms_menu.py` script to be executable. On how to do this, please refer to the Installation section.


### Features
- establishing initial protein (or protein-ligand complex) structure
 - downloading a protein structure directly from Protein Data Bank
 - using a protein structure that was earlier downloaded and/or somehow modified
 - choosing which ligands are to be included in the system which will be simulated
 - choosing if metal ions are to be retained for MD (if they are present in the crystal structure - user will must provide parameters for them though)
 - choosing if crystal waters are to be retained for MD (if they are present in the crystal structure - user will must add hydrogen atoms though)
 - reminding user that he should use functional oligomeric structure of the protein
- preparing topology and coordinate files for Amber
 - processing chosen ligands and protein with pdb4amber
 - choosing protein force field
 - choosing water force field
 - choosing size of a solvation shell
 - creating topology and coordinate files
- preparing input files for Amber
 - choosing routine for simulations (full simulations - minimization, heating, equilibration and production or only a single step-simulation)
 - choosing QM/MM parameters
  - providing custom QM/MM namelist file
  - choosing basic QM/MM parameters (QM atoms, spin, charge, QM Hamiltonian)
  - changing current or adding custom parameters
 - choosing MD parameters
  - default MD parameters for each step are Provided
  - changing values of current MD parameters and the ability to add custom ones (though they must work with Amber codes)
- running MD Simulations
 - where simulations should be run - queue or terminal
 - Amber code which will be run - Sander or PMEMD
 - running mode - serial or parallel codes


### Contributing

If you are interested in contributing to MDMS, please either contact me at szymon.zaczek@edu.p.lodz.pl or create pull request on Github.


### License

[MIT](https://github.com/szymonzaczek/MDMS/blob/master/LICENSE)


### Authors

* **Szymon Zaczek**
