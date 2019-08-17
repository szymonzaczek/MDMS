import os
import fnmatch
import pandas as pd
import numpy as np
import re
import subprocess
import readline
import pybel
from Bio.PDB import *
from pathlib import Path

# allowing tab completion of files' paths
readline.parse_and_bind("tab: complete")

# test if pdb4amber works
try:
    # global is declared - it will be checked upon when pdb4amber is supposed to start
    global pdb4amber_test
    # pdb4amber test - running it and checking output if it contains string is enough
    subprocess.run(['pdb4amber > out_1.txt 2>&1'], shell=True)
    if 'age: pdb4amber' not in open('out_1.txt').read():
        raise Exception
    pdb4amber_test = True
    # removing files that were required for tests
    os.remove(Path('out_1.txt'))
except:
    pdb4amber_test = False


def file_naming():
    # getting name for a control file, which will containg all info
    global filename
    filename_inp = Path(input('Please, provide name for the file that will contain every piece of information for running MDMS. '
                              '\nKeep in mind that if a file with that exact name exists, it will be overwritten.\n'
                              'Please, provide name of the file:\n'))
    filename = filename_inp
    if filename.exists():
        os.remove(filename)


def save_to_file(content, filename):
    # saving to a control file
    with open(filename, 'a') as file:
        file.write(content)


def read_file(filename):
    # reading files
    with open(filename, 'r') as file:
        return file.read()


def file_check(file):
    # checking, if a file exists
    test = file.exists()
    return test


def download_pdb(user_input_id):
    # downloading pdb
    pdbl = PDBList()
    pdbl.retrieve_pdb_file(
        user_input_id,
        pdir='.',
        file_format='pdb',
        overwrite=True)


def stop_interface():
    # enforce stopping the entire interface
    global stop_generator
    stop_generator = True


def read_remark_pdb():
    # retrieving pdb file name from control file
    control = read_file(filename)
    pdb = 'pdb\s*=\s*(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    # creating list into which all of the remark lines will be appended
    pdb_remark = []
    # reading which lines starts with remark and saving it to a list
    with open(f"{pdb_filename}", 'r') as file:
        for line in file:
            # looking for lines starting with remark and appending them to a
            # list
            if line.startswith('REMARK'):
                pdb_remark.append(line.strip())
    if pdb_remark:
        return pdb_remark
    else:
        return None


def read_het_atoms_pdb():
    # retrieving pdb file name from control file
    control = read_file(filename)
    pdb = 'pdb\s*=\s*(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    # cCreating list into which all of the hetatm lines will be appended
    pdb_hetatoms = []
    with open(f"{pdb_filename}", 'r') as file:
        for line in file:
            # looking for lines starting with hetatm and appending them to a
            # list
            if line.startswith('HETATM'):
                pdb_hetatoms.append(line.strip())
    # het atoms will only be saved if there are any het_atoms
    if pdb_hetatoms:
        # saving het_atoms to a csv file - it will be easier to read it then
        with open('het_atoms.csv', 'w') as f:
            f.write('\n'.join(pdb_hetatoms))
        # converting list to a string
        pdb_hetatoms = '\n'.join(pdb_hetatoms)
        return pdb_hetatoms
    else:
        return None


def init_pdb():
    # getting pdb structure
    USER_CHOICE_STRUC = (
        "\nPlease, provide information whether you have already downloaded the PDB file wthat will be investigated, \n"
        "or would you like to retrieve it from RSCB website by providing its PDB ID?\n"
        "- press 'y' if you have already downloaded your PDB file\n"
        "- press 'n' if you haven't downloaded your PDB file yet\n")
    while True:
        try:
            user_input_struc = str(input(USER_CHOICE_STRUC).lower())
            if user_input_struc == 'y':
                # PDB structure provided by user
                while True:
                    try:
                        print("Provide path to your PDB file: \n")
                        pdb_path = Path(input())
                        if file_check(pdb_path) == False:
                            raise Exception
                        elif file_check(pdb_path):
                            break
                    except Exception:
                        print(
                            'The path that you have provided is not valid. Please, provide the correct path to the given file.')
                print(f'\nThe path that you provided: {pdb_path}')
                save_to_file(f"pdb = {pdb_path}\n", filename)
            elif user_input_struc == 'n':
                # PDB structure downloaded from RCSB
                USER_INPUT_ID = (f"Please, provide PDB ID (4 characters) of the species that you would like to investigate.\n")
                while True:
                    try:
                        user_input_id = str(input(USER_INPUT_ID))
                        char_in_string = []
                        # Checking, if input has only 4 alphanumeric characters
                        for i, c in enumerate(user_input_id):
                            char_in_string.append(str(i + 1))
                            if str.isalnum(c):
                                pass
                            else:
                                raise ValueError
                        if char_in_string[-1] != '4':
                            raise ValueError
                        # checking if a file containing this pdb id exists
                        download_pdb(user_input_id)
                        break
                    except ValueError:
                        print(
                            'The input that you have provided is not a valid PDB ID. It must consist of exactly 4 alphanumeric characters.\n')
                # finding a file containing given PDB ID, in order to put it
                # into a prep file
                pdb_file_name = f"*{user_input_id}*"
                # this list is required for checking if there are multiple
                # files containing the same PDB ID
                pdbs = []
                while True:
                    for file in os.listdir('.'):
                        if fnmatch.fnmatch(file, pdb_file_name):
                            # saving names of the files containing given PDB ID
                            # to control file
                            pdbs.append(file)
                    # checking if there are multiples files withh the same PDB
                    # ID
                    if len(pdbs) > 1:
                        # this list will contain index numbers from pdbs list
                        pdbs_ind = []
                        last_el_pdbs = pdbs[-1]
                        len_pdbs = pdbs.index(last_el_pdbs)
                        prompt = (
                            'It appears that there are multiple files that contain PDB ID that you '
                            'specified in the current directory. To assure proper working of the software,'
                            ' you should proceed with only one file. \nWhich is the file that you would '
                            'like to proceed with?')
                        USER_CHOICE_PDB = (
                            'Please, provide the number assigned to the file which you would like to proceed with:\n')
                        print(prompt)
                        for x in pdbs:
                            print(f"{pdbs.index(x)}. {x}")
                            pdbs_ind.append(pdbs.index(x))
                        while True:
                            # user must decide with which file he will proceed
                            # with
                            try:
                                user_input_pdb = int(input(USER_CHOICE_PDB))
                                if user_input_pdb in pdbs_ind:
                                    pdbs = pdbs[user_input_pdb]
                                    # # making sure that the structure ends with pdb
                                    # pdb_renamed = re.sub(r'ent', 'pdb', pdbs)
                                    # os.rename(pdbs, pdb_renamed)
                                    # saving final choice
                                    save_to_file(f"pdb = {pdbs}\n", filename)
                                    break
                            except BaseException:
                                print(
                                    'The input that you provided is not a correct number. Please, provide a valid input')
                        break
                    else:
                        save_to_file(f"pdb = {pdbs[0]}\n", filename)
                        break
            else:
                raise Exception
            break
        except Exception:
            print(
                "The input that you've provided is not valid. Please, provide a valid input.")


def protein_chains_choice():
    # if there are multiple chains specified in PDB, make a choice which will be used - strip the ones that are not used
    # reading pdb file
    control = read_file(filename)
    pdb = 'pdb\s*=\s*(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    # creating object of PDBParser
    p = PDBParser()
    # getting pdb structure
    structure = p.get_structure('X', f'{pdb_filename}')
    # getting list of chains
    chains_list = Selection.unfold_entities(structure, 'C')
    chains_amount = len(chains_list)
    # getting names of chains
    chains_names_string = ''
    # take only the first mode
    for model in structure:
        for chain in model:
            chains_names_string = chains_names_string + str(chain)
    # formatting chains string
    chains_names_string = chains_names_string.replace('<Chain id=', '')
    # turning chains string to a list
    chains_names_list = chains_names_string.split('>')
    # removing empty entry
    chains_names_list = list(filter(None, chains_names_list))
    # if there are no info about chains or there is only a single chain, chains_list have one element; thus, program
    # should proceed on choosing chains only if there is more than one element in chains_lsit
    if chains_amount > 1:
        # list for storing chains for simulations
        chains = []
        USER_CHOICE_CHAINS = (f'\nChoosing protein chains\n'
                              f'There are {chains_amount} different chains in the provided PDB file.\n'
                              f'Each chain identify different molecular chains. For instance, if there are 4 chains in '
                              f'the PDB file, 3 of them might be different polypeptides, whereas one might be a ligand.\n'
                              f'Right now, you will make choice about protein chains.\n'
                              f'Ligands entries will be processed separately.\n'
                              f'Please, consider carefully which chains should be in the simulated model.\n'
                              f'There are following unique protein chains identifiers:\n'
                              f'{chains_names_list}\n'
                              f'Which protein chains would you like to retain for MD simulations? (provide their exact name, '
                              f'separating each entry by a comma - at least one chain must be chosen, otherwise an empty'
                              f' system would have been simulated):\n')
        while True:
            try:
                # getting info about chains from user
                user_input_chains = str(input(USER_CHOICE_CHAINS).upper())
                # turning input into a list, ensuring that no matter how much
                # spaces are inserted everything is fine
                input_chains = re.sub(
                    r'\s', '', user_input_chains).split(',')
                # checking if inputted chains are in unique_chains list - if
                # yes, append them to chain list
                for x in input_chains:
                    if x in chains_names_list:
                        chains.append(x)
                # chains are chosen only once - the other idea is to proceed as with ligands
                # ensuring that at least one chain is chosen - then the chains list will not be empty, thus such
                # expression works
                if chains:
                    save_to_file(f"protein_chains = {chains}\n", filename)
                    break
                pass
            except:
                print('Wrong input has been provided.')
    # deprecated - it used pandas for file reading
    """
    # string which will contain atoms and hetatoms
    pdb_atoms = ''
    # clearing pdb so it will only contain atoms or hetatms
    with open(f'{pdb_filename}', 'r') as file:
        for line in file:
            if line.startswith(('ATOM')):
                pdb_atoms = pdb_atoms + line
    # writing pdb_atoms string to a temporary file which will be removed after this step
    with open('atoms_temp.pdb', 'w') as file:
        file.write(pdb_atoms)
    # reading chain info from temp pdb file with pandas
    df = pd.read_csv(f'atoms_temp.pdb', header=None, delim_whitespace=True, usecols=[4])
    # checking if there is only a single chain in the provided pdb
    if df[4].nunique() == 1:
        # there is only one chain - proceed to next functions
        pass
    else:
        # choice must be provided which chains will be used in calculations
        chains_amount = len(df[4].unique())
        unique_chains = df[4].unique().tolist()
        # list for storing chains for simulations
        chains = []
        USER_CHOICE_CHAINS = (f'\nChoosing protein chains\n'
                              f'There are {chains_amount} different chains in the provided PDB file.\n'
                              f'Each chain identify different molecular chains. For instance, if there are 4 chains in '
                              f'the PDB file, 3 of them might be different polypeptides, whereas one might be a ligand.\n'
                              f'Right now, you will make choice about protein chains.\n'
                              f'Ligands entries will be processed separately.\n'
                              f'Please, carefully consider which chains will be considered in the simulated model.\n'
                              f'There are following unique protein chains identifiers:\n'
                              f'{unique_chains}\n'
                              f'Which protein chains would you like to retain for MD simulations? (provide their exact name, '
                              f'separating each entry by a comma - at least one chain must be chosen, otherwise an empty'
                              f' system would have been simulated):\n')
        while True:
            try:
                # getting info about chains from user
                user_input_chains = str(input(USER_CHOICE_CHAINS).upper())
                # turning input into a list, ensuring that no matter how much
                # spaces are inserted everything is fine
                input_chains = re.sub(
                    r'\s', '', user_input_chains).split(',')
                # checking if inputted chains are in unique_chains list - if
                # yes, append them to chain list
                for x in input_chains:
                    if x in unique_chains:
                        chains.append(x)
                # chains are chosen only once - the other idea is to proceed as with ligands
                #if chains != unique_chains:
                # ensuring that at least one chain is chosen - then the chains list will not be empty, thus such
                # expression works
                if chains:
                    save_to_file(f"protein_chains = {chains}\n", filename)
                    break
                pass
            except:
                print('Wrong input has been provided.')
    # removing temporary file
    os.remove(Path('atoms_temp.pdb'))"""


def missing_atoms_pdb():
    # getting lines starting with remark from a pdb file
    pdb_remark = read_remark_pdb()
    # if there are no pdb_remark, skip this function
    if pdb_remark:
        # looking for missing atoms in remark lines
        missing_atom = ''.join([s for s in pdb_remark if "MISSING ATOM" in s])
        # getting remark nr
        if missing_atom:
            remark = '(REMARK.[0-9]+)'
            remark_match = re.search(remark, missing_atom).group(1)
            # getting string containg all info about missing atoms
            remark_with_missing_atom = '\n'.join(
                ([s for s in pdb_remark if remark_match in s]))
            # making string easier to read
            missing_atom_prompt = re.sub(remark, "", remark_with_missing_atom)
            # if there is a missing atom, print what was found inside pdb file
            # along with warning
            if remark_match is not None:
                print(
                    "\n!!WARNING!!\nIt appears that your PDB file contains missing atoms. They might be added in following steps by"
                    " LEaP, however the better choice would be to use a homology modelling software to do so.\n"
                    "Please, proceed with caution.\n"
                    "Information about missing atom from PDB file: ")
                print(missing_atom_prompt)
                USER_CHOICE_CONT = "Would you like to continue with MDMS execution, or rather right now you would like to " \
                                   "add missing atoms? Please, provide your choice:\n" \
                                   "- press 'y' to continue\n" \
                                   "- press 'n' to quit and go back to the menu\n"
                while True:
                    try:
                        user_input_cont = str(input(USER_CHOICE_CONT)).lower()
                        if user_input_cont == 'y':
                            pass
                        elif user_input_cont == 'n':
                            stop_interface()
                            pass
                        else:
                            raise ValueError
                        break
                    except ValueError:
                        print('Please, provide a valid input. Error 213921')
                    break
            else:
                pass
        else:
            pass


def missing_res_pdb():
    # getting lines starting with remark from a pdb file
    pdb_remark = read_remark_pdb()
    # if there are no pdb_remark, skip this function
    if pdb_remark:
        # looking for missing atoms in remark lines if pdb_remark has any
        # content
        missing_res = ''.join(
            [s for s in pdb_remark if "MISSING RESIDUES" in s])
        if missing_res:
            remark = '(REMARK.[0-9]+)'
            remark_match = re.search(remark, missing_res).group(1)
            # getting string containg all info about missing atoms
            remark_with_missing_res = '\n'.join(
                ([s for s in pdb_remark if remark_match in s]))
            # making string easier to read
            missing_res_prompt = re.sub(remark, "", remark_with_missing_res)
            # handling missing residues with pdbfixer - should be run after choosing to run it
            if remark_match is not None:
                print(
                    "\n!!WARNING!!!\nIt appears that your PDB file contains missing residues. Following information"
                    " were found in the PDB entry:\n", missing_res_prompt)
                # test if pdbfixer is installed
                global pdbfixer_test
                try:
                    subprocess.run(['pdbfixer -h > pdbfixer_test.out'], shell=True)
                    if 'Usage: pdbfixer' not in open('pdbfixer_test.out').read():
                        raise Exception
                    pdbfixer_test = True
                    # removing files required for the test
                    os.remove(Path('pdbfixer_test.out'))
                except:
                    pdbfixer_test = False
                print(f"\nThere is no software available in native AmberTools installation which"
                      f" enable modelling missing residues in PDB files, thus other software "
                      f"must be used for this purpose.\nPerhaps the most powerful tool for "
                      f"modelling missing residues is MODELLER software:\n"
                      f"(A. Fiser, R.K. Do, A. Sali., Modeling of loops in protein structures, Protein Science 9. 1753-1773, 2000, "
                      f"https://salilab.org/modeller/).\n"
                      f"Nonetheless, MDMS might add missing residues to your PDB file using "
                      f"PDBFixer program, which is based on OPenMM software. For this purpose"
                      f" though, you will need a valid PDBFixer installation.\n"
                      f"For installation manual of PDBFixer, please consult the webpage and links provided therein:\n"
                      f"https://github.com/pandegroup/pdbfixer")
                USER_CHOICE_MISSING_RES = (f"Would you like to add missing residues to your PDB file with PDBFixer"
                                           f" automatically (MDMS will do it), or you would rather handle it "
                                           f"differently?\n"
                                           f"- press 'y' if you want to add missing residues using PDBFixer\n"
                                           f"- press 'n' if you want to handle missing residues differently\n")
                if pdbfixer_test:
                    while True:
                        try:
                            user_input_missing_res = str(input(USER_CHOICE_MISSING_RES).lower())
                            if user_input_missing_res == 'y':
                                # save info to control file that pdbfixer should be run
                                save_to_file(f"add_missing_res = True", filename)
                                break
                            elif user_input_missing_res == 'n':
                                # user do not want to add missing residues with pdfixer - nothing is to be run here
                                break
                        except:
                            print('Please, provide valid input.')
                else:
                    print("\nPDBFixer is not installed correctly\n"
                          "If you want MDMS to use PDBFixer to add missing residues to your structure, quit MDMS, install"
                          " PDBFixer and rerun MDMS.\n"
                          "If you want to handle missing residues differently (either you do not require residues that "
                          "are missing in your simulations or you'd rather use different software for modelling missing "
                          "residues), make sure that all of the changes to the PDB file are applied prior to topology "
                          "preparation step.")
                    pass
            # previous version:
            """
            if remark_match is not None:
                print(
                    "\n!!WARNING!!!\nIt appears that your PDB file contains missing residues. Following informations"
                    "were found in the PDB entry:\n", missing_res_prompt)
                USER_CHOICE_MISSING_RES = (f"LEaP is not capable of automatically adding "
                    "missing residues to the structure. \nFor this purpose, you might use MODELLER software:\n"
                    "(A. Fiser, R.K. Do, A. Sali., Modeling of loops in protein structures, Protein Science 9. 1753-1773, 2000, "
                    "https://salilab.org/modeller/).\n"
                    "Only in some very specific cases you might skip adding missing residues to the structure. "
                    "If you are not sure wether it is necessary for your case - most likely it is.\n"
                    "Therefore, prior to proceeding, make sure that you handled missing residues somehow (unless you "
                    "know that there are not necessary).\n"
                    "Are you sure that you might proceed, even though your structure does not have all of the residues "
                    "that have been reported to exist in the PDB entry?\n"
                    "- press 'y' to continue\n"
                    "- press 'n' to quit and go back to the menu\n")
                while True:
                    try:
                        user_input_missing_res = str(input(USER_CHOICE_MISSING_RES).lower())
                        if user_input_missing_res == 'y':
                            break
                        elif user_input_missing_res == 'n':
                            stop_interface()
                    except:
                        print('Please, provide valid input')
            """


def sym_operations_prompt():
    # Reminding user that he must perform crystallographic operations prior to next steps
    # reading pdb file
    control = read_file(filename)
    pdb = 'pdb\s*=\s*(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    # prompt that will be displayed to the user
    USER_CHOICE_OL = f"\n!!WARNING!!\n" \
        f"Oligomeric structure of functional protein\n" \
        f"Prior to proceeding to preparing topology and input coordinates, you need to make" \
        f" sure that your structure has a fully functional oligomeric structure.\nFor instance, active site might be " \
        f"fully formed only if there are 2 (or even more) mnonomeric units of the protein within the studied oligomer. " \
        f"Symmetry operations on PDB files might be performed within various software, such as PyMOL or Swiss-PdbViewer.\n" \
        f"For more info on what oligomeric structure you should proceed with, please, consult the paper " \
        f"that reported obtaining {pdb_filename} crystal structure.\n" \
        f"If you need to make any changes, please make them directly in {pdb_filename} file and run MDMS once you're " \
        f"ready.\n" \
        f"Are you sure that {pdb_filename} has an appropriate oligomeric structure?\n" \
        f"- press 'y' to continue\n" \
        f"- press 'n' to quit and go back to the menu\n"
    while True:
        try:
            user_input_ol = str(
                input(USER_CHOICE_OL).lower())
            if user_input_ol == 'y':
                break
            elif user_input_ol == 'n':
                stop_interface()
                break
            pass
        except BaseException:
            print('Please, provide valid input')


def protonation_state_prompt():
    # Reminding user that he must determine protonation states of individual residues prior to MD
    # reading pdb file
    # Reminding user that protonation states of titrable amino acids should be determined; it might be done by Propka
    # from within MDMS
    control = read_file(filename)
    pdb = 'pdb\s*=\s*(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    # testing if Propka is installed
    global propka_test
    try:
        subprocess.run(['propka31 -h > propka_test.out'], shell=True)
        if 'age: propka31' not in open('propka_test.out').read():
            raise Exception
        propka_test = True
        os.remove(Path('propka_test.out'))
    except:
        propka_test = False
    print("\nProtonation states of amino acids\n"
          "There are a few amino acids which can adopt different protonation states while being simulated with Amber.\n"
          "Those are: Asp, Glu, His and Cys.\n"
          "Default protonation states defined in Amber are in most cases correct for near-neutral pH. Nonetheless, "
          "they still should be validated with any of the popular tools for predicting pKa values such as Propka, H++ web server"
          " or pKD web server.\n"
          "MDMS is capable of performing determination of protonation states using Propka3.1 (M. H. M. Olsson, C. R. SØndergaard, M. Rostkowski, J. H. Jensen, J. Chem. Theory Comput. 2011, 7, 525–537.)\n"
          "If Propka is to be used, it must be correctly installed.\n")
    if propka_test:
        # ask user if propka is to be used
        print('Propka is installed properly.\n')
        USER_CHOICE_PS = f"Do you want to use Propka for determination of protonation states of your structure?\n" \
            f"- press 'y' to use Propka\n" \
            f"- press 'n' to skip a determination of protonation states with Propka\n"
        while True:
            try:
                user_input_ps = str(
                    input(USER_CHOICE_PS).lower())
                if user_input_ps == 'y':
                    USER_CHOICE_PH = f"Please, provide pH at which pKa values for amino acids are to be determined:\n"
                    while True:
                        try:
                            user_input_ph = float(input(USER_CHOICE_PH))
                            save_to_file(f'ph = {user_input_ph}\n', filename)
                            break
                        except:
                            print('Please, provide floating point number.')
                    break
                elif user_input_ps == 'n':
                    break
                pass
            except BaseException:
                print('Please, provide valid input')
    else:
        # tell user that he dos not have propka and ask if he protonation states are defined correctly
        print('Propka is not installed properly.\n')
        # prompt that will be displayed to the user
        USER_CHOICE_PS = f"Are you sure that amino acids within {pdb_filename} file have appropriate protonation states?\n" \
            f"If not, please, make all of the changes to protonation states of residues within {pdb_filename} file in " \
            f"another terminal or install Propka and rerun MDMS.\n" \
            f"Do you want to proceed?\n" \
            f"- press 'y' to continue\n" \
            f"- press 'n' to stop and go back to the menu\n"
        while True:
            try:
                user_input_ps = str(
                    input(USER_CHOICE_PS).lower())
                if user_input_ps == 'y':
                    break
                elif user_input_ps == 'n':
                    stop_interface()
                    break
                pass
            except BaseException:
                print('Please, provide valid input')
        pass


def initial_pdb_process():
    # this function will run the initial structure through pdb4amber, in order to make sure that further steps work
    # correctly
    print('\nRight now your PDB will be processed in order to ensure a proper working with Amber software. If there'
          ' are any missing atoms in amino acids, they will be automatically added with pdb4amber program.\n')
    control = read_file(filename)
    pdb = 'pdb\s*=\s*(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_match_split = pdb_match.split('.')[0]
    pdb_filename = pdb_match
    # copying original pdb file
    struc_copy = f"cp {pdb_filename} full_pdb_{pdb_filename}"
    subprocess.run([f"{struc_copy}"], shell=True)
    # remove atoms alternate locations with default settings
    pdb_selaltloc_inp = f"pdb_selaltloc {pdb_filename} > temp1_{pdb_filename}"
    subprocess.run([f"{pdb_selaltloc_inp}"], shell=True)
    # if user wanted to add missing residues with pdbfixer, it is run
    add_miss_res = 'add_missing_res\s*=\s*(.*)'
    add_miss_res_match = re.search(add_miss_res, control)
    # add_miss_res is in the control file only if user decided to add missing residues with pdbfixer
    if add_miss_res_match:
        # running pdbfixer inplace
        pdbfixer_input = f"pdbfixer temp1_{pdb_filename} --output=temp1_{pdb_filename} --add-atoms=none --add-residues"
        subprocess.run([f"{pdbfixer_input}"], shell=True)
    p = PDBParser()
    # loading structure
    structure = p.get_structure('X', f'temp1_{pdb_filename}')
    # creating IO object
    io = PDBIO()
    # assigning structure to IO
    io.set_structure(structure)
    # saving structure - it will not have any REMARK lines etc.
    io.save(f'temp2_{pdb_filename}')
    # determine if instruction to run Propka was saved to control file
    propka = 'ph\s*=\s*(.*)'
    propka_match = re.search(propka, control).group(1)
    if propka_match:
        ph = float(propka_match)
        # run Propka - it is not run if test for running propka was not passed
        # asp: 3.80
        model_pkas = {
            'ASP': 7.10,
            'GLU': 4.50,
            'HIS': 6.50,
            'CYS': 9.00,
            'LYS': 10.50,
        }
        altered_resnames = {
            'ASP': 'ASH',
            'GLU': 'GLH',
            'HIS': 'HIP',
            'CYS': 'CYM',
            'LYS': 'LYN',
        }
        # adding titrable residues to a list
        titrable_residues = []
        for key in altered_resnames.keys():
            titrable_residues.append(key)
        # run Propka in a loop, if anything goes wrong - just stop running propka
        while True:
            try:
                residues_to_change = []
                # propka needs pdb as an extension of a file
                propka_structure_name = f'temp2_{pdb_filename}'
                propka_structure_name = propka_structure_name.replace('ent', 'pdb')
                # creating copy of a pdb file for running propka
                subprocess.run([f'cp temp2_{pdb_filename} {propka_structure_name}'], shell=True)
                # running propka
                propka_input = f"propka31 -o {ph} {propka_structure_name} > propka.out"
                subprocess.run([f'{propka_input}'], shell=True)
                # reading output from propka
                propka_output = read_file('propka.out')
                # getting only important result
                propka_result = propka_output[propka_output.find('SUMMARY OF THIS PREDICTION'):]
                # removing the first line
                propka_result = "\n".join(propka_result.split("\n")[1:])
                # iterating over lines in propka result
                for line in propka_result.splitlines():
                    # iterating over titrable residues
                    for residue in titrable_residues:
                        # if titrable residue is found in line
                        if residue in line:
                            # split line content into list
                            line_list = line.split()
                            # get the fourth element of the list - this is residue number
                            pka = float(line_list[3])
                            # get the model pKa for this amino acid
                            def_pka = model_pkas.get(residue)
                            # if both model and calculated pka is either less or bigger than pH, do not change anything;
                            # otherwise residue name needs to be changed
                            if (pka > ph and def_pka > ph) or (pka < ph and def_pka < ph):
                                pass
                            else:
                                residues_to_change.append(str(line_list[1]))
                # changing list with residues to change to format that will be passed to pdb-tools - not needed
                #residues_to_change = str(residues_to_change).replace('[', '')
                #residues_to_change = residues_to_change.replace(']', '')
                # reading pdb file
                file = read_file(f'temp2_{pdb_filename}')
                file_renamed_res = ''
                for line in file.splitlines():
                    # only lines that starts with ATOM are releveant here
                    if line.startswith('ATOM'):
                        # getting residue numbers from pdb
                        res_id = str(line[23:26]).replace(' ', '')
                        # if res_id should be changed, change it; if not, append line to a string
                        if res_id in residues_to_change:
                            # getting old_resname
                            old_resname = str(line[17:20])
                            # replace old resname with new resname
                            line = str(line).replace(old_resname, altered_resnames.get(old_resname))
                            # append changed line to a string
                            file_renamed_res = file_renamed_res + '\n' + line
                        else:
                            file_renamed_res = file_renamed_res + '\n' + line
                    # if the line does not start with ATOM, append line to a string
                    else:
                        file_renamed_res = file_renamed_res + '\n' + line
                # remove the first line
                file_renamed_res = "\n".join(file_renamed_res.split("\n")[1:])
                # after applying all changes, save content to a file
                if Path(f'temp2_{pdb_filename}').exists():
                    os.remove(Path(f'temp2_{pdb_filename}'))
                with open(f'temp2_{pdb_filename}', 'w') as file:
                    file.write(file_renamed_res)
                break
            except:
                print('Something went wrong with running Propka. For more information, see Propka output files.')
    # renumber atoms, chains, residues
    pdb_sort_inp = f"pdb_sort temp2_{pdb_filename} > temp3_{pdb_filename}"
    subprocess.run([f"{pdb_sort_inp}"], shell=True)
    # tidy up a molecule
    pdb_tidy_inp = f"pdb_tidy temp3_{pdb_filename} > {pdb_filename}"
    subprocess.run([f"{pdb_tidy_inp}"], shell=True)
    # remove temp1, temp2, temp3
    try:
        os.remove(Path(f"temp1_{pdb_filename}"))
        os.remove(Path(f"temp2_{pdb_filename}"))
        os.remove(Path(f"temp3_{pdb_filename}"))
    except:
        pass
    # further steps might not be necessary
    """
    # setting temperature factor (pdb_b) to 10.0 and occupancy (pdb_occ) to 1.00
    # preparing pipe
    pdb_edit_input_1 = f"pdb_occ {pdb_filename} > temp_{pdb_filename}"
    # running pipe
    subprocess.run([f"{pdb_edit_input_1}"], shell=True)
    pdb_edit_input_2 = f"pdb_b temp_{pdb_filename} > temp2_{pdb_filename}"
    subprocess.run([f"{pdb_edit_input_2}"], shell=True)
    # removing temp file
    os.remove(Path(f"temp_{pdb_filename}"))
    """
    """
    # if pdb4amber works, execute it directly from within MDMS
    if pdb4amber_test:
        # HERE THE NAMING SEEMS TO BE SCREWED
        pdb4amber_input = f"pdb4amber -i full_pdb_{pdb_filename} -o processed_{pdb_match_split}.pdb"
        # running pdb4amber
        subprocess.run([f"{pdb4amber_input}"], shell=True)
    # if pdb4amber does not work, it must be run manually by user
    else:
        struc_path = Path(f"processed_{pdb_filename}")
        if struc_path:
            # if its true, even though pdb4amber does not work from within MDMS, user has already run it
            pass
        else:
            print(f"\n!!WARNING!!\n"
                  f"There were some problems with running pdb4amber from within MDMS.\n"
                  f"If you installed Ambertools previously and it suddenly stopped working, it might be due to "
                  f"the clash of Python versions - MDMS uses Python 3.6, whereas pdb4amber was written in Python 2.7.\n"
                  f"This issue usually occurs on HPC facilities which uses environmental modules feature alongside "
                  f"your own installation of Python.\n"
                  f"If that might be true in your case, for a moment please choose Python 2.7 as a default Python"
                  f"interpreter (i. e. by loading the appropriate module).\n"
                  f"Please also make sure that pdb4amber is installed correctly (just follow Amber Manual on how to "
                  f"install Ambertools).\nAt this point you should be able to use pdb4amber in the terminal.\n"
                  f"In such case, just copy the content of  struc_pdb4amber.in file into terminal and press"
                  f"enter. As a result, you will obtain processed PDB structure' file which will be ready for further"
                  f"steps.")
            process_input = ('struc_pdb4amber.in')
            process_input_path = Path(process_input)
            if process_input_path.exists():
                os.remove(process_input_path)
            # input for pdb4amber
            pdb4amber_input = f"pdb4amber -i full_pdb_{pdb_filename} -o processed_{pdb_match_split}.pdb"
            # input for pdb4amber written to the file
            with open(process_input, 'w') as file:
                file.write(pdb4amber_input)
            print(f"\nYou will now be redirected to the menu of MDMS. Please, quit MDMS and process PDB file "
                  f"from within the terminal, and then provide it as the initial structure for your system"
                  f" of interests")
            # optional saving info about processing of initial struc with pdb4amber
            # save_to_file()
            stop_interface()
    # output from pdb4amber replaces original pdb file - if its done at the end, its possible to check if output from
    # pdb4amber exists
    if Path(f"processed_{pdb_match_split}.pdb").exists:
        renaming = f"mv processed_{pdb_match_split}.pdb {pdb_filename}"
        subprocess.run([f"{renaming}"], shell=True)
    # removing anything apart from ATOM, HETATM, TER and END entries
    entries_allowed = ['ATOM', 'HETATM', 'TER', 'END']
    # empty string to which we will append updated PDB
    pdb_modified = ''
    with open(f"{pdb_filename}", 'r') as file:
        for line in file:
            line_content = line.split()
            # if a first line is in entries_allowed, keep it
            if line_content[0] in entries_allowed:
                pdb_modified = pdb_modified + line
    # remove first line from pdb_modified - it is an empty line
    #pdb_modified = pdb_modified.split('\n', 1)[-1]
    # overwrite pdb_modified as pdb_filename
    with open(f"{pdb_filename}", 'w') as file:
        file.write(pdb_modified)
    # setting temperature factor and occupancy to 0
    with open(f"{pdb_filename}", 'r') as file:
        lines = file.readlines()
    # empty list, which will have modified lines
    new_list = []
    for x in lines:
        line_content = list(x)
        if line_content[0] == 'A' or line_content[0] == 'H':
            # turning string into a list
            # those exact positions are occupancies and b factor entries
            line_content[54] = ' '
            line_content[55] = ' '
            line_content[56] = '1'
            line_content[57] = '.'
            line_content[58] = '0'
            line_content[59] = '0'
            line_content[60] = ' '
            line_content[61] = ' '
            line_content[62] = '1'
            line_content[63] = '.'
            line_content[64] = '0'
            line_content[65] = '0'
            new_line = ''.join(line_content)
            new_list.append(new_line)
        else:
            new_list.append(x)
    # saving modified PDB entry
    with open(f"{pdb_filename}", 'w') as file:
        for x in new_list:
            file.write(x)
    """

def ligands_pdb():
    # getting het_atms from pdb file
    het_atoms = read_het_atoms_pdb()    # it will only get executed if there are hetatoms records in PDB
    if het_atoms:
        # crating a list with unique res names
        unique_res_list = []
        for line in het_atoms.splitlines():
            # checking if a current resname is already in unique_res_list
            if line[17:20] not in unique_res_list:
                # append new resname to unique_res_list
                unique_res_list.append(line[17:20])
        """
        # reading het_atoms as columns - since finding unique residues are
        # sought after, 4 first columns are enough
        df = pd.read_csv(f'het_atoms.csv', header=None, delim_whitespace=True, usecols=[0, 1, 2, 3], na_filter=False)
        # changing naming of columns
        df.columns = ['type', 'atom_nr', 'atom_name', 'residue_name']
        # getting unique residues
        unique_res = df.residue_name.unique()
        unique_res = unique_res.tolist()
        # creating another list that will contain only worthwile ligands
        unique_ligands = unique_res"""
        unique_ligands = unique_res_list
        # removing waters from unique residues
        water_list = ['HOH', 'WAT']
        # remove common metal atoms from unique residues - they will be
        # addressed later on
        metal_list = [
            'K',
            'CA',
            'MN',
            'CO',
            'NA',
            'FE',
            'MG',
            'SR',
            'BA',
            'NI',
            'CU',
            'ZN',
            'CD']
        # remove common leftovers from experiments from unique residues
        exp_leftovers_list = [
            'SCN',
            'ACT',
            'EDO',
            'CL',
            'PGE',
            'GOL',
            'PG4',
            'PEG',
            'P6G',
            'OLC',
            '1PE',
            'CYN',
            'I',
            'NO3']
        # cleaning unique_ligands list so that will only contain ligands that
        # should be acted upon

        for x in metal_list:
            for y in unique_ligands:
                # check if any part of x is in y
                if x in y:
                    # remove whitespaces from y, to have a match ONLY if x and y are the same EXACT strings
                    z = y.replace(' ', '')
                    # if z and x are exactly the same, remove y from unique_ligands
                    if x == z:
                        unique_ligands.remove(y)
        for x in water_list:
            if x in unique_ligands:
                unique_ligands.remove(x)
        for x in metal_list:
            if x in unique_ligands:
                unique_ligands.remove(x)
        # creating a list with leftovers and appending data
        leftovers_list = []
        for x in exp_leftovers_list:
            for y in unique_ligands:
                # check if any part of x is in y
                if x in y:
                    # remove whitespaces from y, to have a match ONLY if x and y are the same EXACT strings
                    z = y.replace(' ', '')
                    # if z and x are exactly the same, remove y from unique_ligands
                    if x == z:
                        leftovers_list.append(x)
        USER_CHOICE_LEFTOVERS = (f"\nLeftovers from experiments\n"
                                 f"There are some residues in your PDB files that might be regarded as a common leftovers"
                                 f" from experimental determination of a protein structure.\n"
                                 f"Those residues are: {leftovers_list}\n"
                                 f"Since those residues are a common leftovers from experiments, they are likely to be "
                                 f"not relevant in your simulations. Nevertheless, you should refer to the original "
                                 f"paper that reported the structure to find out the origin of those residues.\n"
                                 f"Do you want to remove all of the residues that are a common leftovers from experiments, "
                                 f"or you would like to include any of them in your simulations?\n"
                                 f"- press 'y' if you want to remove them all\n"
                                 f"- press 'n' if you want to retain any of those residues in MD simulation\n")
        # if there are leftovers, user decides if he wants to keep any of those residues for MD
        if leftovers_list:
            while True:
                try:
                    user_input_leftovers = str(input(USER_CHOICE_LEFTOVERS).lower())
                    if user_input_leftovers == 'y':
                        for x in exp_leftovers_list:
                            if x in unique_ligands:
                                unique_ligands.remove(x)
                        break
                    elif user_input_leftovers == 'n':
                        # nothing to be done - leftovers are left in ligands list and will be processed in a second by a user
                        break
                except:
                    print('Please, provide valid input.')
        unique_ligands_str = '\n'.join(unique_ligands)
        nr_unique_ligands = len(unique_ligands)
        USER_CHOICE_LIGANDS = (f"\nChoosing ligands\n"
                               f"There are {nr_unique_ligands} unique residues in your PDB file which are not recognized"
                               f" as amino acids, metal ions or water molecules.\n"
                               f"Those residues are most likely ligands, which might be included in the system which"
                               f" will be simulated.\n"
                               f"You should only use ligands that are directly involved in the process that you are "
                               f"interested in.\n"
                               f"If you are not sure whether to include a ligand or not in simulations, refer to the "
                               f"original paper which reported the structure that you are working with.\n"
                               f"Moreover, each ligand that will be retained for simulations will require parametrization,"
                               f" but MDMS will guide you through that in a moment.\n"
                               f"Which residues you would like to keep for simulations? "
                               f"Unique residues are:\n"
                               f"{unique_ligands_str}\n"
                               f"Please specify, which residues will be treated as ligands in your simulation (provide their exact name, "
                               f"separating each entry by a comma - if you decide to not include ligands, just press enter):\n")
        # table for storing ligands kept for simulations, which are present in
        # pdb
        ligands = []
        # loop for choosing which ligands to keep
        while True:
            try:
                # getting input ligands from users
                user_input_ligands = str(input(USER_CHOICE_LIGANDS).upper())
                # turning input into a list, ensuring that no matter how much
                # spaces are inserted everything is fine
                input_ligands = re.sub(
                    r'\s', '', user_input_ligands).split(',')
                # checking if inputted residues are in unique_ligands list - if
                # yes, appending them to ligands list
                for x in input_ligands:
                    if x in unique_ligands:
                        ligands.append(x)
                # this loop ensures that user picked all the ligands that he
                # wanted
                USER_CHOICE_LIG_CONT = (
                    f"Would you like to add more ligands, or would you like to continue to next steps?\n"
                    f"- press 'a' in order to add more ligands\n"
                    f"- press 'c' in order to continue to the next step\n")
                while True:
                    try:
                        # if user decides to keep adding, procedure is repeated
                        if len(ligands) == 0:
                            print('You have not chosen any ligands yet for your simulations.\n')
                        else:
                            print(f"\nSo far, you've chosen following residues to be included as ligands in your simulations: {ligands}.\n")
                        user_input_lig_cont = str(
                            input(USER_CHOICE_LIG_CONT).lower())
                        if user_input_lig_cont == 'a':
                            user_input_ligands = str(
                                input(USER_CHOICE_LIGANDS).upper())
                            # turning input into a list
                            input_ligands = re.sub(
                                r'\s', '', user_input_ligands).split(',')
                            for x in input_ligands:
                                if x in unique_ligands:
                                    # checking, if specified ligand is already
                                    # present in ligands list
                                    if x not in ligands:
                                        ligands.append(x)
                        elif user_input_lig_cont == 'c':
                            # if user decides to finish, ligands are saved to
                            # the control file, if they exist
                            if ligands:
                                save_to_file(f"ligands = {ligands}\n", filename)
                            # lines containing specified ligands are saved to
                            # separate pdb files
                            for x in ligands:
                                ligand_pdb = '\n'.join(
                                    [s for s in het_atoms.splitlines() if x in s])
                                with open(f"{x}_raw.pdb", "w") as f:
                                    f.write(ligand_pdb)
                            break
                    except BaseException:
                        pass
                break
            except BaseException:
                print("You've provided wrong residues")
                pass
        if (ligands):
            print(f"\nLigands that will be included in your system are: \n{ligands}\n")
            hydrogens_prompt()


def metals_pdb():
    # getting het_atms from pdb file
    het_atoms = read_het_atoms_pdb()
    # it will only get executed if there are hetatoms records in PDB
    if het_atoms:
        # getting het atms as csv
        df = pd.read_csv(f'het_atoms.csv', header=None, delim_whitespace=True, usecols=[0, 1, 2, 3], na_filter=False)
        # changing naming of columns
        df.columns = ['type', 'atom_nr', 'atom_name', 'residue_name']
        # metal list that was used in ligands_pdb function
        metal_list = [
            'K',
            'CA',
            'MN',
            'CO',
            'NA',
            'FE',
            'MG',
            'SR',
            'BA',
            'NI',
            'CU',
            'ZN',
            'CD']
        # getting unique residues
        unique_res = df.residue_name.unique()
        unique_res = unique_res.tolist()
        # creating another list that will contain only metal ligands
        unique_metals = []
        for x in metal_list:
            if x in unique_res:
                unique_metals.append(x)
        unique_metals_string = ', '.join(unique_metals)
        USER_CHOICE_METALS = f"\nMetal ions handling\n" \
            f"There are following metal ions in your PDB structure: \n{unique_metals_string}." \
            f"\nObtaining force field parameters for metal ions " \
            f"is outside of scope of this program but you might follow tutorials written by Pengfei Li and Kenneth M. Merz Jr., " \
            f"which are available on Amber Website (http://ambermd.org/tutorials/advanced/tutorial20/index.htm).\n" \
            f"Please keep in mind that sometimes metal ions play an important role in proteins' functioning and ommitting them " \
            f"in MD simulations will provide unrealistic insights. Nonetheless, metal ions might also be just leftovers after " \
            f"experiments (metal ions are normally present in water solutions, from which protein structures are obtained).\n" \
            f"If you do not know if metal ions that are present in your structure are relevant, make a visual inspection of " \
            f"your structure and try to determine if this metal is strongly coordinated by the protein. " \
            f"If it is mostly coordinated " \
            f"by water or it is placed right next to negatively charged amino acid (such as C - terminus), you're good to " \
            f"skip it. Otherwise, most likely you should include it in your system.\n" \
            f"Do you want to retain metal ions for MD simulations? \nIt will require your further manual input outside of this " \
            f"interface:\n" \
            f"- press 'y' to retain metal ions for MD simulations\n" \
            f"- press 'n' not to include metal ions in your MD simulations\n" \
        # if there are metals in pdb, there is a choice if they stay for MD
        # or they are removed
        if unique_metals:
            while True:
                try:
                    user_input_metals = str(input(USER_CHOICE_METALS).lower())
                    if user_input_metals == 'y':
                        # metals are cut out to a separate PDB and info is
                        # saved in a control file
                        save_to_file(f"metals = {unique_metals}\n", filename)
                        # lines containing specified ligands are saved to
                        # separate pdb files
                        print(f"\n!!WARNING!!"
                              f"\nPlease, remember to put parameters for metal ions into tleap input file - otherwise "
                              f"you will be unable to get topology.\n")
                        for x in unique_metals:
                            metals_pdb = '\n'.join(
                                [s for s in het_atoms.splitlines() if x in s])
                            with open(f"{x}.pdb", "w") as f:
                                f.write(metals_pdb)
                        # MCPB.py should be run after protein and ligands have all necessary hydrogens
                        break
                    elif user_input_metals == 'n':
                        # metals will be ignored - no further action required
                        break
                except BaseException:
                    print('You have provided wrong input.')
        pass


def waters_pdb():
    # getting hetatoms from pdb file
    het_atoms = read_het_atoms_pdb()
    # it will only get executed if there are hetatoms records in PDB
    if het_atoms:
        # getting hetatoms as csv
        df = pd.read_csv(f'het_atoms.csv', header=None, delim_whitespace=True, usecols=[0, 1, 2, 3])
        # changing naming of columns
        df.columns = ['type', 'atom_nr', 'atom_name', 'residue_name']
        # list containing names of water residues
        water_list = ['HOH', 'WAT']
        # getting unique residues
        unique_res = df.residue_name.unique()
        unique_res = unique_res.tolist()
        # creating another list that will contain naming of water residues that
        # are present in the pdb
        unique_water = []
        for x in water_list:
            if x in unique_res:
                unique_water.append(x)
        # taking each water molecule from pdb and putting them in a single
        # string
        if unique_water:
            for x in unique_water:
                single_water_pdb = '\n'.join([s for s in het_atoms.splitlines() if x in s])
                water_pdb = ''.join(single_water_pdb)
            waters_number = len(water_pdb.split('\n'))
            USER_CHOICE_WATERS = f"\nCrystal water handling" \
                f"\nThere are {waters_number} water molecules in your structure.\n" \
                f"Water molecules that are present in PDB structures are leftovers from experiments carried out in order to obtain" \
                f" protein's structure. There is no straightforward answer if they should be kept for MD simulations or not - " \
                f"basically water around proteins should equilibrate rather fast and their origin (either from experiment or" \
                f"added with some software) should not matter that much. Noteworthy, even if you want to keep crystal waters " \
                f"for MD, A LOT more waters will need to be added in order to ensure a proper solvation of the protein. " \
                f"Retaining water molecules that were discovered within experiment is strongly advised if water molecules " \
                f"play a role in enzymatic catalysis or they strongly stabilize the protein's structure. Nonetheless, the choice is yours. \n" \
                f"!WARNING!\n" \
                f"If you decide to include crystallographic waters for MD simulations, you will need to manually add hydrogens " \
                f"to the PDB with those waters (for this purpose you could use Avogadro, Pymol, GaussView etc.).\n" \
                f"Would you like to retain water molecules located within experiment for your MD simulations?\n" \
                f"- press 'y' if you want to retain them\n" \
                f"- press 'n' if you want to delete water molecules originally present in your structure\n" \
                # if there are waters in the pdb, user needs to make a decision
            if unique_water:
                while True:
                    try:
                        user_input_waters = str(
                            input(USER_CHOICE_WATERS).lower())
                        if user_input_waters == 'y':
                            # saving crystallographic waters to a separate file
                            with open(f"{x}.pdb", "w") as f:
                                f.write(water_pdb)
                            # saving info about crystallographic waters to a
                            # control file
                            save_to_file(f"waters = {unique_water}\n", filename)
                            # prompt if user wants to add hydrogens with pybel or another software
                            USER_CHOICE_HYD_ADD_WAT = f"\nAdding hydrogen atoms to water molecules\n" \
                                f"MDMS is capable of adding hydrogen atoms to water molecules using Pybel library. You" \
                                f" can either use it, or add hydrogen atoms in another software.\n" \
                                f"Would you like to have hydrogen added to water molecules using Pybel library?\n" \
                                f"- press 'y' if you want to have hydrogens added to water using Pybel (automatic)\n" \
                                f"- press 'n' if you want to add hydrogens atoms to water molecules with another software" \
                                f" (you will need to do this manually though)\n" \
                                f"Please, provide your choice:\n"
                            while True:
                                try:
                                    user_input_hyd_add_wat = str(input(USER_CHOICE_HYD_ADD_WAT).lower())
                                    if user_input_hyd_add_wat == 'y':
                                        # adding hydrogens to waters with Pybel
                                        mol = pybel.readfile('pdb', f'{x}.pdb')
                                        for y in mol:
                                            # adding hydrogens
                                            y.addh()
                                            # overwriting water file
                                            y.write(format='pdb', filename=f'{x}.pdb', overwrite=True)
                                        # string to which hydrogenated molecule will be appended, in order to format it
                                        # properly
                                        water_temp_string = ''
                                        # keeping only atom or hetatm entries from pdb
                                        with open(f'{x}.pdb', 'r') as file:
                                            a = file.read()
                                            for line in a.splitlines():
                                                if 'ATOM' in line or 'HETATM' in line:
                                                    # replacing atom with hetatm - waters are treated as ligands
                                                    if 'ATOM' in line:
                                                        line = line.replace('ATOM  ', 'HETATM')
                                                    # appending formatted line to a string
                                                    water_temp_string = water_temp_string + '\n' + line
                                        # removing empty line at the beginning
                                        water_temp_string = water_temp_string.split('\n', 1)[-1]
                                        # writing file
                                        with open(f'{x}.pdb', 'w') as file:
                                            file.write(water_temp_string)
                                        # reading cleaned file
                                        df = pd.read_csv(f'{x}.pdb', header=None, delim_whitespace=True)
                                        # displaying 3 digits in x coordinates - if not used, numpy prints tons of
                                        # unnecessary digits
                                        df[6] = df[6].astype(float).map('{:,.3f}'.format)
                                        # adding spaces to x coordinates - required for a proper reading of a pdb file
                                        df[6] = df[6].astype(str).str.pad(8, side='left', fillchar=' ')
                                        # creating new column which will count occurences of each atom name
                                        df[11] = df.groupby([2, 5]).cumcount() + 1
                                        # finding out duplicated atom names
                                        df[12] = df[5].duplicated(keep='first')
                                        # if there is a duplicated atom name and residue number, add number from df[11] column
                                        df[2] = np.where(df[12] == True, df[2].astype(str) + df[11].astype(str), df[2])
                                        # remove 2 columns that were only used for finding duplicates and assigning new atom names
                                        df = df.drop(df.columns[[12, 11]], axis=1)
                                        # sorting by residue number and by atom number - each residue will be represented
                                        # as OHH thanks to this
                                        water_sorted = df.sort_values([5, 1])
                                        # changing df to a string - it enables saving content easily
                                        water_sorted_string = water_sorted.to_string(index=False, header=None)
                                        # ensuring that there are no additional spaces at the beginning of each line
                                        water_sorted_string_no_spaces = ''
                                        # iterating over each line
                                        for line in water_sorted_string.splitlines():
                                            # finding out if a first character in a line is a space
                                            if line[0:1].isspace():
                                                line = line[1:]
                                            # appending formatted lines to a new string
                                            water_sorted_string_no_spaces = water_sorted_string_no_spaces + '\n' + line
                                        # removing first line from newly created string
                                        water_sorted_string_no_spaces = water_sorted_string_no_spaces.split('\n', 1)[-1]
                                        # saving
                                        with open(f'{x}_raw.pdb', 'w') as file:
                                            file.write(water_sorted_string_no_spaces)
                                        # removing HOH.pdb - later on, it will contain already formatted data after
                                        # pdb4amber
                                        if Path(f'{x}.pdb').exists():
                                            os.remove(Path(f'{x}.pdb'))
                                        break
                                    else:
                                        # user chose to add hydrogens manually
                                        print(f"\nPlease, add hydrogen atoms to {x}.pdb file prior to proceeding to"
                                              f" topology preparation.\n")
                                        break
                                except:
                                    print('Please, provide valid input')
                                    pass
                            break
                        elif user_input_waters == 'n':
                            # if user decides to omit crystallographic waters,
                            # nothing needs to be done
                            break
                    except BaseException:
                        print('The input that you have provided is not valid')
            pass


def hydrogens_prompt():
    # Reminding that user must add hydrogens to ligands
    # reading control file
    control = read_file(filename)
    ligands = r'ligands\s*=\s*\[(.*)\]'
    ligands_match = re.search(ligands, control)
    # function will only be executed if there were ligands chosen
    if ligands_match:
        # taking only ligands' entries values
        ligands_match = ligands_match.group(1)
        # removing quotes from string
        ligands_string = ligands_match.replace("'", "")
        # removing whitespaces and turning string into a list
        ligands_list = re.sub(r'\s', '', ligands_string).split(',')
        USER_CHOICE_HYDROGENS = (f"Adding hydrogen atoms to ligands\n"
                                 f"You have chosen to include ligands molecules in your system. In order to correctly proceed to MD simulations,"
                                 f" hydrogen atoms must be added to your ligands molecules, whenever necessary.\n"
                                 f"This can be normally done with plenty of software, such as PyMOL, Chimera, LigPrep, Avogadro, etc.\n"
                                 f"Nonetheless, MDMS is capable of adding hydrogens via Python implementation of OpenBabel software - Pybel.\n"
                                 f"If you choose not to use Pybel, you will need to add hydrogen atoms to ligands by yourself.\n"
                                 f"Please note that Pybel fully completes the valence - thus it is not possible to automatically "
                                 f"prepare charged species with it - for doing so, you will need to process ligand files manually.\n"
                                 f"Would you like to have hydrogens added via Pybel?\n"
                                 f"- press 'y' to add hydrogens to ligands using Pybel (it is automatic)\n"
                                 f"- press 'n' to add hydrogens with 3rd party software - you will need to do this manually\n")
        # following clause will be executed only if there are ligands in the
        # control file
        if ligands_list:
            while True:
                try:
                    user_input_hydrogens = str(
                        input(USER_CHOICE_HYDROGENS).lower())
                    # adding hydrogens with pybel
                    if user_input_hydrogens == 'y':
                        for ligand in ligands_list:
                            mol = pybel.readfile('pdb', f'{ligand}_raw.pdb')
                            # iterating over ligands in mol - in case of MDMS there will only be one molecule in mol
                            # but pybel is created this way that it can contain more atoms
                            for x in mol:
                                # adding hydrogens
                                x.addh()
                                # overwriting ligand file
                                x.write(format='pdb', filename=f'{ligand}.pdb', overwrite=True)
                            # empty string, to which we we will append lines
                            ligand_temp_string = ''
                            # keeping only atom or hetatm entries from pdb
                            with open(f'{ligand}.pdb', 'r') as file:
                                a = file.read()
                                for line in a.splitlines():
                                    if 'ATOM' in line or 'HETATM' in line:
                                        # since we act on ligands, if atom line is detected it is replaced
                                        # with hetatm; atoms are added by pybel
                                        if 'ATOM' in line:
                                            line = line.replace('ATOM  ', 'HETATM')
                                        # appending formatted line to a string
                                        ligand_temp_string = ligand_temp_string + '\n' + line
                            # string has an additional empty line at the beginning - this gets rid of it
                            ligand_temp_string = ligand_temp_string.split('\n', 1)[-1]
                            # writing file
                            with open(f'{ligand}.pdb', 'w') as file:
                                file.write(ligand_temp_string)
                            # reading cleaned file
                            df = pd.read_csv(f'{ligand}.pdb', header=None, delim_whitespace=True)
                            # displaying 3 digits in x coordinates - if not used, numpy prints
                            # tons of unnecessary digits
                            df[6] = df[6].astype(float).map('{:,.3f}'.format)
                            # adding spaces to x coordinates - this is required for a proper reading of
                            # a pdb file - exactly 7 spaces are required
                            df[6] = df[6].astype(str).str.pad(8, side='left', fillchar=' ')
                            # creating new column which will count occurence of each atom name
                            df[11] = df.groupby([2]).cumcount()+1
                            # finding out duplicated atom names
                            df[12] = df[2].duplicated(keep=False)
                            # if there is a duplicated atom name, add number from df[11] column
                            df[2] = np.where(df[12]==True, df[2].astype(str) + df[11].astype(str), df[2])
                            # remove 2 columns that were only used for finding duplicates and assigning new atom names
                            df = df.drop(df.columns[[12,11]], axis=1)
                            # sorting at first by residue number, at then by atom number - each residue
                            # will be represented as OHH thanks to this
                            ligand_sorted = df.sort_values([5, 1])
                            # changing df to a string - it enables saving content easily
                            ligand_sorted_string = ligand_sorted.to_string(index=False, header=None)
                            # ensuring that there are no additional spaces at the beginning of each line
                            ligand_sorted_string_no_spaces = ''
                            # iterating over each line
                            for line in ligand_sorted_string.splitlines():
                                # finding out if a first character in a line is a space
                                if line[0:1].isspace():
                                    # if a first character in a line is a string, it is removed
                                    line = line[1:]
                                # appending formatted lines to a new string
                                ligand_sorted_string_no_spaces = ligand_sorted_string_no_spaces + '\n' + line
                            # removing first line from newly created string
                            ligand_sorted_string_no_spaces = ligand_sorted_string_no_spaces.split('\n', 1)[-1]
                            # saving
                            with open(f'{ligand}.pdb', 'w') as file:
                                file.write(ligand_sorted_string_no_spaces)
                        break
                    elif user_input_hydrogens == 'n':
                        print(f'Please, quit MDMS and proceed to adding hydrogens to the ligand file. After you will '
                              f'have done so, you might proceed to the next step of MDMS - topology preparation')
                        stop_interface()
                        break
                    pass
                except BaseException:
                    print('Please, provide valid input')


def chain_processing():
    # getting rid of unnecessary protein chains
    # reading pdb file
    control = read_file(filename)
    pdb = 'pdb\s*=\s*(.*)'
    pdb_match = re.search(pdb, control).group(1)
    # stripping of extension from structure - this way it will be easier to
    # get proper names, i.e. 4zaf_old.pdb
    pdb_match_split = pdb_match.split('.')[0]
    # copying original PDB file so it will be retained after files operations
    #struc_copy = f"cp {pdb_match} {pdb_match_split}_original.pdb"
    #subprocess.run([f"{struc_copy}"], shell=True)
    pdb_filename = pdb_match
    # reading if chain is specified in prep file
    chain = 'protein_chains\s*=\s*\[(.*)\]'
    chain_match = re.search(chain, control)
    # if there is chain info specified, proceed, otherwhise proceed
    if chain_match:
        # taking only chain entries
        chain_match = chain_match.group(1)
        # removing quotes from string
        chain_string = chain_match.replace("'", "")
        # removing whitespaces and turning string into a list
        chain_list = re.sub(r'\s', '', chain_string).split(',')
        # empty list containing info from individual line
        line_content = []
        # empty string containing info about lines with chosen chain identifier - it will be converted to string later on
        pdb_modified = ''
        # find atoms with chain info from chain_list, remove everything else from pdb file
        # read pdb but only if line starts with atom - only protein atoms are considered
        with open(f"{pdb_filename}", 'r') as file:
            for line in file:
                # updating list with content of a current line
                line_content = line.split()
                # if first word in a line is atom, proceed
                if line_content[0] == 'ATOM':
                    # append line content to pdb_modified
                    pdb_modified = pdb_modified + '\n' + line
        # remove the first line from pdb_modified - it is empty line
        pdb_modified = pdb_modified.split('\n', 1)[-1]
        # save pdb_modified so it could be read by pandas
        with open(f"pdb_chain_temp.pdb", 'w') as file:
            file.write(pdb_modified)
        # empty string to which final PDB file will be written
        pdb_refined = ''
        # read pdb_modified with pandas
        df1 = pd.read_csv(f'pdb_chain_temp.pdb', header=None, delim_whitespace=True)
        # creating new dataframe containing only specified chains
        df2 = df1.loc[df1[4].isin(chain_list)]
        # convert dataframe to a string
        pdb_refined = df2.to_string(index=False, header=None)
        # save string to a file as a new pdb file
        with open(pdb_match, 'w') as file:
            file.write(pdb_refined)
        # remove temp file
        os.remove(Path('pdb_chain_temp.pdb'))
    pass


prep_functions = [
    file_naming,
    init_pdb,
    missing_atoms_pdb,
    missing_res_pdb,
    sym_operations_prompt,
    protonation_state_prompt,
    initial_pdb_process,
    protein_chains_choice,
    ligands_pdb,
    metals_pdb,
    waters_pdb,
    chain_processing,
]

methods_generator = (y for y in prep_functions)


def queue_methods():
    # Generator that keeps everything running in the correct order
    next(methods_generator, None)
    global stop_generator
    stop_generator = False
    for x in prep_functions:
        x()
        # if a condition is met, generator is stopped
        if stop_generator:
            # I do not know if this prompt is necessary
            print('\nProgram has not finished normally - it appears that something was wrong with your structure. \nApply changes and try again!\n')
            break
