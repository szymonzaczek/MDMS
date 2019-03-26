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


def read_remark_pdb():
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
                #pdb_remark.append(next(file).strip())
    return pdb_remark

def read_het_atoms_pdb():
    control = read_file(filename)
    pdb = 'pdb.=.(.*)'
    pdb_match = re.search(pdb, control).group(1)
    pdb_filename = pdb_match
    pdb_hetatoms = []
    with open(f"{pdb_filename}", 'r') as file:
        for line in file:
            if line.startswith('HETATM'):
                pdb_remark.append(line.strip())
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
                            #save_to_file(f"pdb = {file}\n", filename)
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
                            #user must decide with which file he will proceed
                            try:
                                user_input_pdb = int(input(USER_CHOICE_PDB))
                                if user_input_pdb in pdbs_ind:
                                    pdbs = pdbs[user_input_pdb]
                                    #saving should be here
                                    print(pdbs)
                                    save_to_file(f"pdb = {pdbs}\n", filename)
                                    break
                            except:
                                print('The input that you provided is not a correct number. Please, provide a valid input')
                        #for x in pdbs:
                           # print(f"The file you have chosen is: {pdbs.index(x)}. {x}")
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
        #Here, add function to ask if user wants to finish at this point
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
            print(
                "\nERROR!!!\nIt appears that your PDB file contains missing residues. LEaP is not capable of automatically adding "
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
    #except:
    #    #This is not really relevant#
    #    print("It appears there is a problem.")

#def ligands_pdb():
#    het_atoms = read_het_atoms_pdb()
#    print(het_atoms)
#    pass



#prep_functions = [file_naming, init_pdb, missing_atoms_pdb, missing_res_pdb, ligands_pdb]
prep_functions = [file_naming, init_pdb, missing_atoms_pdb, missing_res_pdb]

methods_generator = (y for y in prep_functions)

def queue_methods():
    next(methods_generator, None)
    global stop_generator
    stop_generator = False
    for x in prep_functions:#
        x()
        # if a condition is met, generator is stopped
        if stop_generator == True:
            #I do not know if this prompt is necessary
            print('\nProgram has not finished normally - it appears that something was wrong with your structure. \nApply changes and try again!\n')
            break
#