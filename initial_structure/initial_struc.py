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
    filename_inp: str = Path(input('Please, provide name for the file that will contain every piece of information for running SAmber. '
                                   '\nPlease, kepp in mind that if a file with that exact name exists, it will be overwritten.\n'
                                   'Please, provide name of the file:\n'))
    filename = filename_inp
    if filename.exists() == True:
        os.remove(filename)

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


def init_pdb():
    #getting pdb structure
    USER_CHOICE_STRUC = ("Please, provide information whether you have already downloaded the PDB file wthat will be investigated, \n"
                         "or would you like to retrieve it from RSCB website by providing its PDB ID?\n"
                         "• press 'y' if you have already downloaded your PDB file\n"
                         "• press 'n' if you haven't downloaded your PDB file yet\n")
    while True:
        try:
            user_input_struc = str(input(USER_CHOICE_STRUC).lower())
            if user_input_struc == 'y':
                #PDB structure provided by user
                while True:
                    try:
                        print("Provide path to your PDB file: \n")
                        pdb_path = Path(input())
                        if file_check(pdb_path) == False:
                            raise Exception
                        elif file_check(pdb_path) == True:
                            break
                    except Exception:
                        print('The path that you have provided is not valid. Please, provide the correct path to the given file.')
                print(f'\nThe path that you provided: {pdb_path}')
                save_to_file(f"pdb = {pdb_path}\n", filename)
            elif user_input_struc == 'n':
                #PDB structure downloaded from RCSB
                USER_INPUT_ID = (f"Please, provide PDB ID (4 characters) of the species that you would like to investigate.\n")
                while True:
                    try:
                        user_input_id = str(input(USER_INPUT_ID))
                        char_in_string = []
                        #Checking, if input has only 4 alphanumeric characters
                        for i, c in enumerate(user_input_id):
                            char_in_string.append(str(i+1))
                            if str.isalnum(c):
                                pass
                            else:
                                raise ValueError
                        if char_in_string[-1] != '4':
                            raise ValueError
                        #checking if a file containing this pdb id exists
                        download_pdb(user_input_id)
                        break
                    except ValueError:
                        print('The input that you have provided is not a valid PDB ID. It must consist of exactly 4 alphanumeric characters.\n')
                # finding a file containing given PDB ID, in order to put it into a prep file
                pdb_file_name = f"*{user_input_id}*"
                #this list is required for checking if there are multiple files containing the same PDB ID
                pdbs = []
                while True:
                    for file in os.listdir('.'):
                        if fnmatch.fnmatch(file, pdb_file_name):
                            #saving names of the files containing given PDB ID to control file
                            pdbs.append(file)
                    #checking if there are multiples files withh the same PDB ID
                    if len(pdbs) > 1:
                        #this list will contain index numbers from pdbs list
                        pdbs_ind = []
                        print(pdbs)
                        last_el_pdbs = pdbs[-1]
                        len_pdbs = pdbs.index(last_el_pdbs)
                        print(len_pdbs)
                        prompt = ('It appears that there are multiple files that contain PDB ID that you '
                                  'specified in the current directory. To assure proper working of the software,'
                                  ' you should proceed with only one file. \nWhich is the file that you would '
                                  'like to proceed with?')
                        USER_CHOICE_PDB = ('Please, provide the number assigned to the file which you would like to proceed with:\n')
                        print(prompt)
                        for x in pdbs:
                            print(f"{pdbs.index(x)}. {x}")
                            pdbs_ind.append(pdbs.index(x))
                        while True:
                            #user must decide with which file he will proceed with
                            try:
                                user_input_pdb = int(input(USER_CHOICE_PDB))
                                if user_input_pdb in pdbs_ind:
                                    pdbs = pdbs[user_input_pdb]
                                    #saving final choice
                                    print(pdbs)
                                    save_to_file(f"pdb = {pdbs}\n", filename)
                                    break
                            except:
                                print('The input that you provided is not a correct number. Please, provide a valid input')
                        break
                    else:
                        save_to_file(f"pdb = {pdbs[0]}\n", filename)
                        break
            else:
                raise Exception
            break
        except Exception:
            print("The input that you've provided is not valid. Please, provide a valid input. Tu mamy blad")

def missing_atoms_pdb():
    #getting lines starting with remark from a pdb file
    pdb_remark = read_remark_pdb()
    #looking for missing atoms in remark lines
    missing_atom = ''.join([s for s in pdb_remark if "MISSING ATOM" in s])
    #getting remark nr
    if missing_atom:
        remark = '(REMARK.[0-9]+)'
        remark_match = re.search(remark, missing_atom).group(1)
        #getting string containg all info about missing atoms
        remark_with_missing_atom = '\n'.join(([s for s in pdb_remark if remark_match in s]))
        #making string easier to read
        missing_atom_prompt = re.sub(remark, "", remark_with_missing_atom)
        #if there is a missing atom, print what was found inside pdb file along with warning
        if remark_match != None:
            print("\nWARNING!!!\nIt appears that your PDB file contains missing atoms. They might be added in following steps by"
                  " LEaP, however the better choice would be to use a homology modelling software to do so.\n"
                  "Please, proceed with caution.\n"
                  "Information about missing atom from PDB file: ")
            print(missing_atom_prompt)
            USER_CHOICE_CONT = "Would you like to continue with SAmber execution, or rather right now you would like to " \
                               "add missing atoms? Please, provide your choice:\n" \
                               "• press 'y' to continue\n" \
                               "• press 'n' to quit\n"
            while True:
                try:
                    user_input_cont = str(input(USER_CHOICE_CONT)).lower()
                    if user_input_cont == 'y':
                        pass
                    elif user_input_cont == 'n':
                        stop_interface()
                        break
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
    # looking for missing atoms in remark lines
    missing_res = ''.join([s for s in pdb_remark if "MISSING RESIDUES" in s])
    # if there are missing residues, following lines will be executed
    if missing_res:
        remark = '(REMARK.[0-9]+)'
        remark_match = re.search(remark, missing_res).group(1)
        # getting string containg all info about missing atoms
        remark_with_missing_res = '\n'.join(([s for s in pdb_remark if remark_match in s]))
        # making string easier to read
        missing_res_prompt = re.sub(remark, "", remark_with_missing_res)
        # if there is a missing atom, print what was found inside pdb file along with warning
        if remark_match != None:
            print("\nERROR!!!\nIt appears that your PDB file contains missing residues. LEaP is not capable of automatically adding "
                "missing residues to the structure. \nFor this purpose, you might use MODELLER software:\n"
                "  (A. Fiser, R.K. Do, A. Sali., Modeling of loops in protein structures, Protein Science 9. 1753-1773, 2000, "
                "https://salilab.org/modeller/).\n"
                "Prior to proceeding, make sure that there are no missing residues in your structure. \nApply changes to the "
                "PDB file that will be provided into the SAmber and run SAmber again with altered initial structure.\n"
                "Information about missing residues from PDB file: ")
            print(missing_res_prompt)
            stop_interface()
    else:
        #If there are no missing residues, everything is fine
        pass

def ligands_pdb():
    #getting het_atms from pdb file
    het_atoms = read_het_atoms_pdb()
    #reading het_atoms as columns - since finding unique residues are sought after, 4 first columns are enough
    df = pd.read_csv(f'het_atoms.csv', header=None, delim_whitespace=True, usecols=[0, 1, 2, 3])
    #changing naming of columns
    #df.columns = ['type', 'atom_nr', 'atom_name', 'residue_name', 'chain', 'residue_nr', 'x', 'y', 'z', 'occupancy', 'temp_factor', 'element']
    df.columns = ['type', 'atom_nr', 'atom_name', 'residue_name']
    #getting unique residues
    unique_res = df.residue_name.unique()
    unique_res = unique_res.tolist()
    #creating another list that will contain only worthwile ligands
    unique_ligands = unique_res
    #removing waters from unique residues
    water_list = ['HOH', 'WAT']
    #remove common metal atoms from unique residues - they will be addressed later on
    metal_list = ['K', 'CA', 'MN', 'CO', 'NA', 'FE', 'MG', 'SR', 'BA', 'NI', 'CU', 'ZN', 'CD']
    #remove other common from unique residues - leftovers after experiments
    exp_leftovers_list = ['SCN', 'ACT', 'EDO', 'CL', 'PGE', 'PG4', 'PEG', 'P6G', 'OLC', '1PE', 'CYN', 'I', 'NO3']
    #cleaning unique_ligands list so that will only contain ligands that should be acted upon
    for x in water_list:
        if x in unique_ligands:
            unique_ligands.remove(x)
    for x in metal_list:
        if x in unique_ligands:
            unique_ligands.remove(x)
    for x in exp_leftovers_list:
        if x in unique_ligands:
            unique_ligands.remove(x)
    unique_ligands_str = '\n'.join(unique_ligands)
    nr_unique_ligands = len(unique_ligands)
    USER_CHOICE_LIGANDS = (f"There are {nr_unique_ligands} unique residues in your PDB file which are not amino acids and waters.\n"
                           f"Each ligand that will be retained for simulations, will require parametrization.\n"
                           f"Which residues you would like to keep for simulations? "
                           f"Unique residues are:\n"
                           f"{unique_ligands_str}\n"
                           f"Please specify, which residues will be treated as ligands in your simulation (provide their exact name, "
                           f"separating each entry by a comma - if you decide to not include ligands, just press enter):\n")
    #table for storing ligands kept for simulations, which are present in pdb
    ligands = []
    #loop for choosing which ligands to keep
    while True:
        try:
            #getting input ligands from users
            user_input_ligands = str(input(USER_CHOICE_LIGANDS).upper())
            #turning input into a list, ensuring that no matter how much spaces are inserted everything is fine
            input_ligands = re.sub(r'\s', '', user_input_ligands).split(',')
            #checking if inputted residues are in unique_ligands list - if yes, appending them to ligands list
            for x in input_ligands:
                if x in unique_ligands:
                    ligands.append(x)
            #this loop ensures that user picked all the ligands that he wanted
            while True:
                USER_CHOICE_LIG_CONT = (f"So far, you've chosen following residues to be included as ligands in your simulations: {ligands}.\n"
                                        f"Would you like to add more ligands, or would you like to continue?\n"
                                        f"• press 'a' in order to add more ligands\n"
                                        f"• press 'c' in order to continue to next step\n")
                try:
                    #if user decides to keep adding, procedure is repeated
                    user_input_lig_cont = str(input(USER_CHOICE_LIG_CONT).lower())
                    if user_input_lig_cont == 'a':
                        user_input_ligands = str(input(USER_CHOICE_LIGANDS).upper())
                        #turning input into a list
                        input_ligands = re.sub(r'\s', '', user_input_ligands).split(',')
                        for x in input_ligands:
                            if x in unique_ligands:
                                #checking, if specified ligand is already present in ligands list
                                if x not in ligands:
                                    ligands.append(x)
                    elif user_input_lig_cont == 'c':
                        #if user decides to finish, ligands are saved to the control file
                        save_to_file(f"ligands = {ligands}\n", filename)
                        #lines containing specified ligands are saved to separate pdb files
                        for x in ligands:
                            ligands_pdb = '\n'.join([s for s in het_atoms if x in s])
                            with open(f"{x}.pdb", "w") as f:
                                f.write(ligands_pdb)
                        break
                except:
                    pass
            break
        except:
            print("You've provided wrong residues")
            pass
    print(f"Ligands that will be included in your system are: {ligands}")
    pass

def metals_pdb():
    #getting het_atms from pdb file
    het_atoms = read_het_atoms_pdb()
    #getting het atms as csv
    df = pd.read_csv(f'het_atoms.csv', header=None, delim_whitespace=True, usecols=[0, 1, 2, 3])
    #changing naming of columns
    df.columns = ['type', 'atom_nr', 'atom_name', 'residue_name']
    #metal list that was used in ligands_pdb function
    metal_list = ['K', 'CA', 'MN', 'CO', 'NA', 'FE', 'MG', 'SR', 'BA', 'NI', 'CU', 'ZN', 'CD']
    #getting unique residues
    unique_res = df.residue_name.unique()
    unique_res = unique_res.tolist()
    #creating another list that will contain only metal ligands
    unique_metals = []
    for x in metal_list:
        if x in unique_res:
            unique_metals.append(x)
    unique_metals_string = ', '.join(unique_metals)
    USER_CHOICE_METALS = f"\nThere are following metal ions in your PDB structure: {unique_metals_string}. " \
        f"Obtaining force field parameters for metal ions " \
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
        f"• press 'y' to retain metal ions for MD simulations\n" \
        f"• press 'n' not to include metal ions in your MD simulations\n" \
    #if there are metals in pdb, there is a choice if they stay for MD or they are removed
    if unique_metals:
        while True:
            try:
                user_input_metals = str(input(USER_CHOICE_METALS).lower())
                if user_input_metals == 'y':
                    #metals are cut out to a separate PDB and info is saved in a control file
                    save_to_file(f"metals = {unique_metals}\n", filename)
                    # lines containing specified ligands are saved to separate pdb files
                    for x in unique_metals:
                        metals_pdb = '\n'.join([s for s in het_atoms if x in s])
                        with open(f"{x}.pdb", "w") as f:
                            f.write(metals_pdb)
                    break
                elif user_input_metals == 'n':
                    #metals will be ignored - no further action required
                    break
            except:
                print('You have provided wrong input.')
    pass

def waters_pdb():
    # getting het_atms from pdb file
    het_atoms = read_het_atoms_pdb()
    # getting het atms as csv
    df = pd.read_csv(f'het_atoms.csv', header=None, delim_whitespace=True, usecols=[0, 1, 2, 3])
    # changing naming of columns
    df.columns = ['type', 'atom_nr', 'atom_name', 'residue_name']
    #list containing names of water residues
    water_list = ['HOH', 'WAT']
    #getting unique residues
    unique_res = df.residue_name.unique()
    unique_res = unique_res.tolist()
    #creating another list that will contain naming of water residues that are present in the pdb
    unique_water = []
    for x in water_list:
        if x in unique_res:
            unique_water.append(x)
    #taking each water molecule from pdb and putting them in a single string
    for x in unique_water:
        single_water_pdb = '\n'.join([s for s in het_atoms if x in s])
        waters_pdb = ''.join(single_water_pdb)
    waters_number = len(waters_pdb.split('\n'))
    USER_CHOICE_WATERS = f"\nThere are {waters_number} water molecules in your structure.\n" \
        f"Water molecules that are present in PDB structures are leftovers from experiments carried out in order to obtain" \
        f"protein's structure. There is no straightforward answer if they should be kept for MD simulations or not - " \
        f"basically water around proteins should equilibrate rather fast and their origin (either from experiment or" \
        f"added with some software) should not matter that much. Noteworthy, even if you want to keep crystal waters" \
        f"for MD, A LOT more waters will need to be added in order to ensure a proper solvation of the protein." \
        f"Retaining water molecules that were discovered within experiment is strongly advised important if water molecules" \
        f"play a role in enzymatic catalysis or they somehow stabilize the protein's structure. Nonetheless, the choice is yours. \n" \
        f"Would you like to retain water molecules located within experiment for your MD simulations?\n" \
        f"• press 'y' if you want to retain them\n" \
        f"• press 'n' if you want to delete water molecules originally present in your structure\n" \
    #if there are waters in the pdb, user needs to make a decision
    if unique_water:
        while True:
            try:
                user_input_waters = str(input(USER_CHOICE_WATERS).lower())
                if user_input_waters == 'y':
                    #saving crystallographic waters to a separate file
                    with open(f"{x}.pdb", "w") as f:
                        f.write(waters_pdb)
                    #saving info about crystallographic waters to a control file
                    save_to_file(f"waters = {unique_water}\n", filename)
                    break
                elif user_input_waters == 'n':
                    #if user decides to omit crystallographic waters, nothing needs to be done
                    break
            except:
                print('The input that you have provided is not valid')
    pass


def hydrogens_prompt():
    # Reminding that user must add hydrogens to ligands
    control = read_file(filename)
    ligands = 'ligands.*=.*\[(.*)\]'
    ligands_match = re.search(ligands, control).group(1)
    # removing quotes from string
    ligands_string = ligands_match.replace("'", "")
    # removing whitespaces and turning string into a list
    ligands_list = re.sub(r'\s', '', ligands_string).split(',')
    USER_CHOICE_HYDROGENS = (f"\n!!WARNING!!\n" \
        f"You have chosen to include ligands molecules in your system. In order to correctly proceed to MD simulations," \
        f" hydrogen atoms must be added to your ligands molecules, whenever necessary. Adding hydrogens is outside of " \
        f"scope of SAmber, therefore you must use other software to do so, such as OpenBabel, PyMOL, Chimera, LigPrep," \
        f" Avogadro or any other that suites you best. In order to best utilize SAmber, just edit PDB files that were generated" \
        f" with SAmber and overwrite them when you will have already added hydrogens.\n" \
        f"In order to proceed, all of the ligands must have all of the necessary hydrogen atoms.\n" \
        f"Have you added hydrogen atoms to all of the ligands?\n" \
        f"• press 'y' to continue\n" \
        f"• press 'n' to stop SAmber run\n")
    # following clause will be executed only if there are ligands in the control file
    if ligands_list:
        while True:
            try:
                user_input_hydrogens = str(input(USER_CHOICE_HYDROGENS).lower())
                if user_input_hydrogens == 'y':
                    break
                elif user_input_hydrogens == 'n':
                    stop_interface()
                    break
                pass
            except:
                print('Please, provide valid input')


prep_functions = [file_naming, init_pdb, missing_atoms_pdb, missing_res_pdb, ligands_pdb, metals_pdb, waters_pdb, hydrogens_prompt]

methods_generator = (y for y in prep_functions)


def queue_methods():
    #Generator that keeps everything running in the correct order
    next(methods_generator, None)
    global stop_generator
    stop_generator = False
    for x in prep_functions:
        x()
        # if a condition is met, generator is stopped
        if stop_generator == True:
            #I do not know if this prompt is necessary
            print('\nProgram has not finished normally - it appears that something was wrong with your structure. \nApply changes and try again!\n')
            break
    #print('initial struc is finished')