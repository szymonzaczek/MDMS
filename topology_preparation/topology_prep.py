import os
import numpy
import fnmatch
import re
from Bio.PDB import *
from pathlib import Path

def file_naming():
    #getting name for a control file, which will containg all info
    global filename
    filename_inp: str = Path(input('Please, provide a name for the file that will contain every piece of information for running SAmber:\n'))
    filename = filename_inp
    if filename.exists() == True:
        os.remove(filename)

def save_to_file(content, filename):
    #saving to a file
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


def remark_read_pdb():
    #retrieving pdb file name from control file
    control = read_file(filename)
    pdb = 'pdb.=.(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    pdb_remark = []
    #reading which lines starts with remark and saving it to a list
    with open(f"{pdb_filename}", 'r') as file:
        for line in file:
            if line.startswith('REMARK'):
                pdb_remark.append(line.strip())
    #writing list containing all remark lines to a file - should not be necessary
    #with open('remark.txt', 'w') as file_handler:
    #    for item in pdb_remark:
    #        file_handler.write("{}\n".format(item))
    return pdb_remark



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
                save_to_file(f"pdb = {pdb_path}", filename)
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
                        download_pdb(user_input_id)
                        break
                    except ValueError:
                        print('The input that you have provided is not a valid PDB ID. It must consist of exactly 4 alphanumeric characters.\n')
                # finding a file containing given PDB ID, in order to put it into a prep file
                pdb_file_name = f"*{user_input_id}*"
                for file in os.listdir('.'):
                    if fnmatch.fnmatch(file, pdb_file_name):
                        save_to_file(f"pdb = {file}", filename)
            else:
                raise Exception
            break
        except Exception:
            print("The input that you've provided is not valid. Please, provide a valid input.")



def missing_atoms_pdb():
    #getting lines starting with remark from a pdb file
    pdb_remark = remark_read_pdb()
    #looking for missing atoms in remark lines
    missing_atom = ''.join([s for s in pdb_remark if "MISSING ATOM" in s])
    #getting remark nr
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
        #Here, add function that will ensure that user knows what he's doing

def missing_res_pdb():
    # getting lines starting with remark from a pdb file
    pdb_remark = remark_read_pdb()
    # looking for missing atoms in remark lines
    missing_res = ''.join([s for s in pdb_remark if "MISSING RESIDUES" in s])
    # getting remark nr
    remark = '(REMARK.[0-9]+)'
    remark_match = re.search(remark, missing_res).group(1)
    # getting string containg all info about missing atoms
    remark_with_missing_res = '\n'.join(([s for s in pdb_remark if remark_match in s]))
    # making string easier to read
    missing_res_prompt = re.sub(remark, "", remark_with_missing_res)
    # if there is a missing atom, print what was found inside pdb file along with warning
    if remark_match != None:
        print(
            "\nERROR!!!\nIt appears that your PDB file contains missing residues. LEaP is not capable of automatically adding "
            "missing residues to the structure. \nFor this purpose, you might use MODELLER software:\n"
            "(A. Fiser, R.K. Do, A. Sali., Modeling of loops in protein structures, Protein Science 9. 1753-1773, 2000, "
            "https://salilab.org/modeller/).\n"
            "Prior to proceeding, make sure that there are no missing residues in your structure. \nApply changes to the "
            "PDB file that will be provided into the SAmber and run SAmber again with altered initial structure.\n"
            "Information about missing residues from PDB file: ")
        print(missing_res_prompt)
        #stopping interface, if there are missing residues
        stop_interface()
        #global stop_generator
        #stop_generator = True

def duplicate_res_pdb():#
    pass



prep_functions = [file_naming, init_pdb, missing_atoms_pdb, missing_res_pdb, duplicate_res_pdb]

methods_generator = (y for y in prep_functions)

def queue_methods():
    next(methods_generator, None)
    global stop_generator
    stop_generator = False
    for x in prep_functions:
        x()
        # if a condition is met, generator is stopped
        if stop_generator == True:
            print('\nProgram has not finished normally - it appears that something was wrong with your structure. \nApply changes and try again!\n')
            break
