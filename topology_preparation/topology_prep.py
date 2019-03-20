import os
import numpy
from Bio.PDB import *
from pathlib import Path

def file_naming():
    global filename
    filename_inp: str = Path(input('Please, provide a name for the file that will contain every piece of information for running SAmber:\n'))
    filename = filename_inp
    if filename.exists() == True:
        os.remove(filename)

def save_to_file(content, filename):
    with open(filename, 'a') as file:
        file.write(content)

def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()
#fdsf

def file_check(file):
    test = file.exists()
    return test

def download_pdb(user_input_id):
    pdbl = PDBList()
    pdbl.retrieve_pdb_file(user_input_id, pdir='.', file_format='pdb')



def init_structure():
    USER_CHOICE_STRUC = ("Please, provide information whether you have already downloaded the PDB file wthat will be investigated, \n"
                         "or would you like to retrieve it from RSCB website by providing its PDB ID?\n"
                         "• press 'y' if you have already downloaded your PDB file\n"
                         "• press 'n' if you haven't downloaded your PDB file yet\n")
    while True:
        try:
            user_input_struc = str(input(USER_CHOICE_STRUC).lower())
            if user_input_struc == 'y':
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
                save_to_file(f"mol = {pdb_path}", filename)
            elif user_input_struc == 'n':
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
                        #retrieve_pdb_file(user_input_id)
                        download_pdb(user_input_id)
                        break
                    except ValueError:
                        print('The input that you have provided is not a valid PDB ID. It must consist of exactly 4 alphanumeric characters.\n')

            else:
                raise Exception
            break
        except Exception:
            print("The input that you've provided is not valid. Please, provide a valid input.")


prep_functions = [file_naming, init_structure]

methods_generator = (y for y in prep_functions)

def queue_methods():
    next(methods_generator, None)
    for x in prep_functions:
        x()
