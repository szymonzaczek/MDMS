import os
import fnmatch
import pandas as pd
import re
import subprocess
from Bio.PDB import *
from pathlib import Path


def file_naming():
    #getting name for a control file, which will containg all info
    global filename
    while True:
        try:
            filename_inp: str = Path(input('Please, provide a path to the file that contains every piece of information for running SAmber (it should be already generated):\n'))
            filename = filename_inp
            if filename.exists() == True:
                break
            else:
                print('There is no such file.')
        except:
            print('Please, provide valid input')


def save_to_file(content, filename):
    #saving to a control file
    with open(filename, 'a') as file:
        file.write(content)


def read_file(filename):
    #reading files
    with open(filename, 'r') as file:
        return file.read()


def file_check(file):
    #checking, if a file exists
    test = file.exists()
    return test


def download_pdb(user_input_id):
    #downloading pdb
    pdbl = PDBList()
    pdbl.retrieve_pdb_file(user_input_id, pdir='.', file_format='pdb', overwrite=True)


def stop_interface():
    #enforce stopping the entire interface
    global stop_generator
    stop_generator = True


def read_remark_pdb():
    #retrieving pdb file name from control file
    control = read_file(filename)
    pdb = 'pdb.=.(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    #creating list into which all of the remark lines will be appended
    pdb_remark = []
    #reading which lines starts with remark and saving it to a list
    with open(f"{pdb_filename}", 'r') as file:
        for line in file:
            # looking for lines starting with remark and appending them to a list
            if line.startswith('REMARK'):
                pdb_remark.append(line.strip())
    return pdb_remark


def read_het_atoms_pdb():
    # retrieving pdb file name from control file
    control = read_file(filename)
    pdb = 'pdb.=.(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    #cCreating list into which all of the hetatm lines will be appended
    pdb_hetatoms = []
    with open(f"{pdb_filename}", 'r') as file:
        for line in file:
            #looking for lines starting with hetatm and appending them to a list
            if line.startswith('HETATM'):
                pdb_hetatoms.append(line.strip())
    # saving het_atoms to a csv file - it will be easier to read it then
    with open('het_atoms.csv', 'w') as f:
        f.write('\n'.join(pdb_hetatoms))
    return pdb_hetatoms


def hydrogen_check():
    # Checking if hydrogens are added to ligands file
    control = read_file(filename)
    ligands = 'ligands.*=.*\[(.*)\]'
    ligands_match = re.search(ligands, control).group(1)
    # removing quotes from string
    ligands_string = ligands_match.replace("'", "")
    # removing whitespaces and turning string into a list
    ligands_list = re.sub(r'\s', '', ligands_string).split(',')
    # storing info about how many atoms are in ligands
    atoms_amount = []
    # storing info about how many hydrogen atoms are in ligands
    hydrogens_amount = []
    # following clause will be executed only if there are ligands in the control file
    if ligands_list:
        for ligand in ligands_list:
            # reading 3rd column (pandas numbering - 2nd) from ligand.pdb - if there are no hydrogens in residue names, there are no hydrogens in the whole file
            df = pd.read_csv(f'{ligand}.pdb', header=None, delim_whitespace=True, usecols=[2])
            # getting info how many atoms are in a ligand
            df_len = len(df.iloc[:, 0])
            # storing info in list, which will contain info about all ligands
            atoms_amount.append(df_len)
            # establishing if there are hydrogens in atom names
            hydrogen_match = (df[df.iloc[:, 0].str.match('H')])
            # counting how many hydrogens were in a ligand
            hydrogen_count = len(hydrogen_match.iloc[:, 0])
            # storing info about amount of hydrogens in a list
            hydrogens_amount.append(hydrogen_count)
        print(hydrogens_amount[0])
        print(type(hydrogens_amount[0]))
        for x in range(0, len(ligands_list)):
            if hydrogens_amount[x] == 0:
                USER_CHOICE_HYDROGENS = (f"Even though there are {atoms_amount[x]} atoms in your ligand, there are no "
                                         f"hydrogen atoms. Please keep in mind that all of the ligands MUST have all the"
                                         f"necessary hydrogen atoms in their structure")


            #USER_CHOICE_HYDROGENS = f"There are f{len(ligands_list)} in your system. They"
            #for x in range(0, df_len):
            #    hydrogen_present = df.iloc[[x, 0]].str.contains('H')
            #    if hydrogen_present:
            #        hydrogens_amount = hydrogens_amount + 1
            #print(hydrogens_amount)
            #hydrogen_mask = df[df.columns[0]].str.contains('O')
            #print(hydrogen_mask)
            #ligand_file = read_file(f"{ligand}.pdb")
            #print(ligand_file)
    pass


def ligands_parameters():
    #finding ligands residues in prep file
    control = read_file(filename)
    ligands = 'ligands.*=.*\[(.*)\]'
    ligands_match = re.search(ligands, control).group(1)
    #removing quotes from string
    ligands_string = ligands_match.replace("'", "")
    #removing whitespaces and turning string into a list
    ligands_list = re.sub(r'\s', '', ligands_string).split(',')
    #getting necessary infor for antechamber input
    USER_CHOICE_CHARGE_MODEL = f"Please specify the charge model that you would like to apply to your ligands. If you want" \
        f"to employ RESP charges, you will need to manually modify antechamber input files.\n" \
        f"Please note that AM1-BCC charge model is a recommended choice.\n" \
        f"Following options are available:\n" \
        f"• 'cm1' - CM1 charge model\n" \
        f"• 'esp' - ESP (Kollman) charge model\n" \
        f"• 'gas' - Gasteiger charge model\n" \
        f"• 'bcc' - AM1-BCC charge model\n" \
        f"• 'cm2' - CM2 charge model\n" \
        f"• 'mul' - Mulliken charge model\n" \
        f"Please, provide one of the options from available answers (single-quoted words specified above):\n"
    USER_CHOICE_ATOM_TYPES = f"Please, specify which atom types you would like to assign to your ligands.\n" \
        f"Please note that GAFF2 is a recommended choice.\n" \
        f"Following options are available:\n" \
        f"• 'gaff2' - General Amber Force Field, version 2\n" \
        f"• 'gaff' - General Amber Force Field, older version of GAFF2\n" \
        f"• 'bcc' - for AM1-BCC atom types\n"
    #the whole function will only do something, if ligands_list have anything in it
    charge_model = ''
    atoms_type = ''
    REMINDER = f"\n!!WARNING!!\n" \
        f"You have chosen to include ligands molecules in your system. In order to correctly proceed to MD simulations," \
        f" hydrogen atoms must be added to your ligands molecules, whenever necessary. Adding hydrogens is outside of " \
        f"scope of SAmber, therefore you must use other software to do so, such as OpenBabel, PyMOL, Chimera, LigPrep," \
        f" Avogadro or any other that suites you best. In order to best utilize SAmber, just edit PDB files that were generated" \
        f"throughout SAmber usage and overwrite them when you will have already added hydrogens.\n" \
        f"In order to proceed, all of the ligands must have all of the necessary hydrogen atoms.\n" \
        f"Have you added hydrogen atoms to all of the ligands?\n" \
        f"• press 'y' to continue" \
        f"• press 'n' to stop SAmber run" \
        f"or manually " \
        f""
    if ligands_list:
        #prompting user that he MUSTS have hydrogens already added to the
        # specifying charge model
        while True:
            try:
                user_input_charge_model = str(input(USER_CHOICE_CHARGE_MODEL).lower())
                if user_input_charge_model == 'cm1':
                    charge_model = 'cm1'
                elif user_input_charge_model == 'esp':
                    charge_model = 'esp'
                elif user_input_charge_model == 'gas':
                    charge_model = 'gas'
                elif user_input_charge_model == 'bcc':
                    charge_model = 'bcc'
                elif user_input_charge_model == 'cm2':
                    charge_model = 'cm2'
                elif user_input_charge_model == 'mul':
                    charge_model = 'mul'
                save_to_file(f"charge_model = {charge_model}\n", filename)
                break
            except:
                print('The input that you have provided is not valid.')
        #specifying atom types
        while True:
            try:
                user_input_atom_types = str(input(USER_CHOICE_ATOM_TYPES).lower())
                if user_input_atom_types == 'bcc':
                    atoms_type = 'bcc'
                elif user_input_atom_types == 'gaff':
                    atoms_type = 'gaff'
                elif user_input_atom_types == 'gaff2':
                    atoms_type = 'gaff2'
                save_to_file(f"atoms_type = {atoms_type}\n", filename)
                break
            except:
                print('The input that you have provided is not valid')
        #specifying charges and multiplicity for each ligand
        lig_charges = []
        lig_multiplicities = []
        for x in ligands_list:
            # those must be looped on, since each ligand might have different charge and multiplicity
            USER_CHOICE_CHARGE = f"Please, provide the net charge of {x} ligand (integer value):\n"
            USER_CHOICE_MULTIPLICITY = f"Please, provide multiplicity of {x} ligand (positive integer value):\n"
            while True:
                try:
                    user_input_charge = int(input(USER_CHOICE_CHARGE))
                    user_input_multiplicity = int(input(USER_CHOICE_MULTIPLICITY))
                    if user_input_multiplicity < 1:
                        raise Exception
                    lig_charges.append(user_input_charge)
                    lig_multiplicities.append(user_input_multiplicity)
                    break
                except:
                    print("The input that you have provided is not valid")
        save_to_file(f"ligands_charges = {lig_charges}\n", filename)
        save_to_file(f"ligands_multiplicities = {lig_multiplicities}\n", filename)
    pass


def antechamber_parmchk_input():
    #finding ligands residues in control file
    control = read_file(filename)
    ligands = 'ligands.*=.*\[(.*)\]'
    ligands_match = re.search(ligands, control).group(1)
    #removing quotes from string
    ligands_string = ligands_match.replace("'", "")
    #removing whitespaces and turning string into a list
    ligands_list = re.sub(r'\s', '', ligands_string).split(',')
    #getting charge_model info
    charge_model = 'charge_model\s*=\s*([a-z]*[A-Z]*[1-9]*)'
    charge_model_match = re.search(charge_model, control).group(1)
    #getting atom_types info
    atoms_type = 'atoms_type\s*=\s*([a-z]*[A-Z]*[1-9]*)'
    atoms_type_match = re.search(atoms_type, control).group(1)
    #finding ligands' charges in control file
    ligands_charges = 'ligands_charges\s*=\s*\[(.*)\]'
    ligands_charges_match = re.search(ligands_charges, control).group(1)
    #removing whitespaces and turning to a list
    ligands_charges_list = re.sub(r'\s', '', ligands_charges_match).split(',')
    #changing individual entries from string to integers
    for x in range(0, len(ligands_charges_list)):
        ligands_charges_list[x] = int(ligands_charges_list[x])
    #finding ligands multiplicities in control file
    ligands_multiplicities = 'ligands_multiplicities\s*=\s*\[(.*)\]'
    ligands_multiplicities_match = re.search(ligands_multiplicities, control).group(1)
    # removing whitespaces and turning to a list
    ligands_multiplicities_list = re.sub(r'\s', '', ligands_multiplicities_match).split(',')
    #changing individual entries from string to integers
    for x in range(0, len(ligands_multiplicities_list)):
        ligands_multiplicities_list[x] = int(ligands_multiplicities_list[x])
    #creating antechamber inputs
    for x in range(0, len(ligands_list)):
        antechamber_input = f"antechamber -fi pdb -fo mol2 -i {ligands_list[x]}.pdb -o {ligands_list[x]}.mol2 -at {atoms_type_match} -c {charge_model_match} -pf y -nc {ligands_charges_list[x]} -m {ligands_multiplicities_list[x]}"
        print(antechamber_input)
        subprocess.run([f"{antechamber_input}"], shell=True)
        parmchk_input = f"parmchk2 -i {ligands_list[x]}.mol2 -o {ligands_list[x]}.frcmod -f mol2 -s {atoms_type_match}"
        print(parmchk_input)
        subprocess.run([f"{parmchk_input}"], shell=True)

def parmchk_input():
    pass


top_prep_functions = [file_naming, hydrogen_check, ligands_parameters, antechamber_parmchk_input]
#prep_functions = [file_naming, init_pdb, missing_atoms_pdb, missing_res_pdb]

methods_generator = (y for y in top_prep_functions)

def queue_methods():
    next(methods_generator, None)
    global stop_generator
    stop_generator = False
    for x in top_prep_functions:
        x()
        # if a condition is met, generator is stopped
        if stop_generator == True:
            #I do not know if this prompt is necessary
            print('\nProgram has not finished normally - it appears that something was wrong with your structure. \nApply changes and try again!\n')
            break