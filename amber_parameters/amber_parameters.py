import os
import pandas as pd
import re
import subprocess
from pathlib import Path


def file_naming():
    # getting name for a control file, which will containg all info
    global filename
    while True:
        try:
            filename_inp: str = Path(input('Please, provide a path to the file that contains every piece of information for running MDMS (it should be already generated):\n'))
            if filename_inp.exists():
                filename = filename_inp
                break
            else:
                print('There is no such file.')
        except BaseException:
            print('Please, provide valid input')


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


def stop_interface():
    # enforce stopping the entire interface
    global stop_generator
    stop_generator = True


def clearing_control():
    # it is passed on right now, since I do not know yet what paremeters will be derived here
    # this function clears control file from what will be inputted with amber_parameters run
    # name of temporary file that will store what is important
    filetemp = 'temp.txt'
    # list of parameters that will be stripped out of control file
    parameters = [
        'qm',
    ]
    # writing content of control file without parameters in parameters list to
    # the temporary file
    with open(f"{filename}") as oldfile, open(filetemp, 'w') as newfile:
        for line in oldfile:
            if not any(parameters in line for parameters in parameters):
                newfile.write(line)
    # replacing control file with temporary file
    os.replace(filetemp, filename)


def qm_or_not():
    # asking user if he wants to perform QM/MM calculations and getting necessary parameters
    USER_CHOICE_QM = f"\nDo you want to perform QM/MM calculations?\nPlease, keep in mind that such simulations" \
        f"are MUCH more computationally expensive than regular MD. However, this is THE ONLY way to capture " \
        f"chemical structures' alterations within AMBER. For observing physical properties though, it is " \
        f"rather advised to use regular MD, which will allow covering bigger timescales.\n" \
        f"Do you want to perform QM/MM calculations?\n" \
        f"- press 'y' if you do\n" \
        f"- press 'n' if you do not and you want to run regular MD\n" \
    # looping QM/MM choice
    while True:
        try:
            user_input_qm = str(input(USER_CHOICE_QM).lower())
            if user_input_qm == 'y':
                # if QM is to be performed, save info to control file
                save_to_file(f"qm = True\n", filename)
                break
            elif user_input_qm == 'n':
                # if not, do not save anything
                break
        except:
            print('Please, provide valid input')


def qm_parameters():
    # reading from control file if there is a qm part and then choose parameters for qm
    # reading control file
    control = read_file(filename)
    # reading if qm was chosn or not
    qm = r'qm\s*=\s*(.*)'
    qm_match = re.search(qm, control)
    # if QM/MM was chosen, ask about parameters
    if qm_match:
        qm_match = qm_match.group(1)
        # defining if user have got qmcontrol file
        USER_CHOICE_QMCONTROL = """\nDo you have a file containig &qmmm namelist with all the necessary information required
for QM/MM simulations? You might have it from the previous MDMS run or by creating your own file following Amber
guidelines. If you do not have it, do not worry - we will create one in a moment!
- press 'y' if you do
- press 'n' if you don't - a file with default parameters will be created in the current directory.
Please, provide your choice:\n """
        while True:
            try:
                user_input_qmcontrol = str(input(USER_CHOICE_QMCONTROL).lower())
                if user_input_qmcontrol == 'y':
                    # define path to qmcontrol file
                    USER_CHOICE_QMPATH = f"Please, provide path to the file that contains parameters for the QM part" \
                        f" for your simulations (it should only contain &qmmm namelist):\n"
                    while True:
                        try:
                            user_input_qmpath = str(input(USER_CHOICE_QMPATH))
                            print(Path(user_input_qmpath))
                            if file_check(Path(user_input_qmpath)) == True:
                                # everything is good an we may close the loop
                                save_to_file(f"qmcontrol = {user_input_qmpath}\n", filename)
                                break
                            elif file_check(Path(user_input_qmpath)) == False:
                                # there is no file with provided path and user is prompted to provide path again
                                print('There is no such file. Please, provide a valid path')
                        except:
                            print('Please, provide a valid input')
                    break
                elif user_input_qmcontrol == 'n':
                    # defining qmatoms
                    USER_CHOICE_QMATOMS = f"Which atoms from your system should be treated with QM methods? Any valid " \
                        f"Amber mask will work (for more info about masks refer to Amber manual).\n" \
                        f"Please, provide your choice (Amber mask formatting is required:\n"
                    while True:
                        try:
                            user_input_qmatoms = str(input(USER_CHOICE_QMATOMS).upper())
                            break
                        except:
                            print('Please, provide valid input')
                    # defining spin
                    USER_CHOICE_QMSPIN = f"What is the spin of the QM part of your system?\n" \
                        f"Please, provide spin value for the QM part of your system (positive integer value):\n"
                    while True:
                        try:
                            user_input_qmspin = int(input(USER_CHOICE_QMSPIN))
                            if user_input_qmspin > 0:
                                break
                        except:
                            print('Please, provide valid input')
                    # defining charge
                    USER_CHOICE_QMCHARGE = f"What is the charge of the QM part of your system?\n" \
                        f"Please, provide charge value for the QM part of your system (integer value):\n"
                    while True:
                        try:
                            user_input_qmcharge = int(input(USER_CHOICE_QMCHARGE))
                            break
                        except:
                            print('Please, provide valid input')
                    # define qmmethod
                    USER_CHOICE_QMMETHOD = f"Which QM method would you like to use? The following options are available:\n" \
                        f"- 'AM1'\n" \
                        f"- 'PM3'\n" \
                        f"- 'RM1'\n" \
                        f"- 'MNDO'\n" \
                        f"- 'PM3-PDDG'\n" \
                        f"- 'MNDOD'\n" \
                        f"- 'AM1D'\n" \
                        f"- 'PM6'\n" \
                        f"- 'DFTB2'\n" \
                        f"- 'DFTB3'\n"
                    qm_methods = ['AM1', 'PM3', 'RM1', 'MNDO', 'PM3-PDDG', 'MNDOD', 'AM1D', 'PM6', 'DFTB2', 'DFTB3']
                    while True:
                        try:
                            user_input_qmmethod = str(input(USER_CHOICE_QMMETHOD).upper())
                            if user_input_qmmethod in qm_methods:
                                break
                        except:
                            print('Please, provide valid input')
                    qm_input = 'qmcontrol.in'
                    # if qm_input already exist, remove it
                    if file_check(Path(qm_input)):
                        os.remove(Path(qm_input))
                    # save qm info to qm_input
                    with open(qm_input, 'w') as file:
                        file.write(f"&qmmm,\n"
                                   f"qmmask = {user_input_qmatoms},\n"
                                   f"spin = {user_input_qmspin},\n"
                                   f"qmcharge = {user_input_qmcharge},\n"
                                   f"qmshake = 0,\n"
                                   f"qm_ewald = 1,\n"
                                   f"qm_pme = 1,\n"
                                   f"qm_theory = {user_input_qmmethod},\n"
                                   f"printcharges = 1,\n"
                                   f"writepdb = 1,\n"
                                   f"/")
                    save_to_file(f"qmcontrol = {qm_input}\n", filename)
                    break
                #break
            except:
                print('Please, provide valid input')


def steps_to_perform():
    # getting info what simulations to perform
    USER_CHOICE_PROCEDURE = "\nIn most cases, the investigated protein/protein-ligand complex should be at first minimized" \
                            ", then heated to the target temperature, equilibrated, and only then a regular production runs " \
                            "should be performed. Nonetheless, for some reasons, you might want to skip minimization, " \
                            "heating  and equilibration (i. e. you might have performed it in another software) and " \
                            "immediately head to production simulations. This is advised only if you know exactly what " \
                            "you are doing though.\n" \
                            "Which procedure for simulations you want to follow?\n" \
                            "- press 'n' for a normal procedure - minimization, heating, equilibration and production\n" \
                            "- press 'p' if you only want to run production simulations\n" \
                            "Please, provide your choice:\n"
    while True:
        try:
            user_input_procedure = str(input(USER_CHOICE_PROCEDURE).lower())
            if user_input_procedure == 'n':
                # if normal procedure is chose, run everything
                steps = ['min', 'heat', 'equi', 'prod']
                break
            elif user_input_procedure == 'p':
                # run only production
                steps = ['prod']
                break
        except:
            print('Please, provide valid input')
    # after loop is closed, save info to the control file
    save_to_file(f"procedure = {steps}\n", filename)
    pass


def default_parameters(step):
    # function storing default parameters for individual simulations steps
    # defining def_params
    def_params = ""
    if step == 'min':
        def_params = """&cntrl
 imin=1, 
 ntx=1,
 irest=0,
 maxcyc=4000, 
 ncyc=2000,
 cut=8.0, 
 ntb=1,  
 ntpr=100,
 nmropt=0, 
 ntr=0,
 ifqnt=0
/"""
    elif step == 'heat':
        def_params = """&cntrl
 imin = 0, #min or md
 irest = 0, #rest or not
 ntx = 1, #reading initial coordinates
 ntb = 1, #periodic box, 1 = constant volume, 2 = constant pressure
 ntp = 0, #constant pressure, 0 = nope, 1 = yep
 cut = 8.0, #cutoff, 8 usually enough - higher needs a lot of computational time
 ntc = 2, #shake definition
 ntf = 2, #shake, bond interactions involving H atoms are omitted
 tempi = 0.0, #initial temp
 temp0 = 300.0, #target temp
 ntt = 3, #thermostat, 3 = Langevind dynamics (probably the best choice atm)
 gamma_ln = 2.0, #collision frequency, it should be a good value
 nstlim = 25000, #nr of steps
 dt = 0.002, #timestep
 ntpr = 100, #how often energy is saved
 ntwx = 500, #how often trajectory is saved
 ntwr = 5000, #how often restart is saved
 ig=-1, #random seed
 ifqnt=0, #qmmm or not
 nmropt=1,#NMR restraints, used to control temperature
/
&wt type='TEMP0', istep1=0, istep2=25000, value1=0.0, value2=300.0 /
&wt type='END' /
"""
    elif step == 'equi':
        def_params = """&cntrl
 imin = 0, 
 irest = 1, 
 ntx = 5,
 ntb = 2, #constant pressure
 ntp = 1,
 taup = 2.0, #pressure relaxation time, should be between 1 to 5
 cut = 8.0, 
 ntc = 2, 
 ntf = 2,
 tempi = 300.0, 
 temp0 = 300.0,
 ntt = 3, 
 gamma_ln = 2.0,
 nstlim = 75000, 
 dt = 0.002,
 ntpr = 500, 
 ntwx = 500, 
 ntwr = 5000,
 ig=-1, 
 ifqnt=0,
 nmropt=0
/"""
    elif step == 'prod':
        def_params = """&cntrl
 imin = 0, 
 irest = 1, 
 ntx = 5,
 ntb = 2,  
 ntp = 1,
 taup = 2.0,
 cut = 8.0, 
 ntc = 2, 
 ntf = 2,
 tempi = 300.0, 
 temp0 = 300.0,
 ntt = 3, 
 gamma_ln = 2.0,
 nstlim = 10000000, 
 dt = 0.002,
 ntpr = 500, 
 ntwx = 2500, 
 ntwr = 20000
 ig=-1, 
 ifqnt=0,
 nmropt=0
/"""
    return def_params



def md_parameters():
    # Determining MD parameters
    # reading info from control file
    control = read_file(filename)
    steps = r'procedure.*=.*\[(.*)\]'
    steps_match = re.search(steps, control).group(1)
    # removing quotes from string
    steps_string = steps_match.replace("'", "")
    # removing whitespaces and turning string into a list
    steps_list = re.sub(r'\s', '', steps_string).split(',')
    # formatting steps, so it will be printed in a nicer way
    steps_dict = {
        'min': 'minimization',
        'heat': 'heating',
        'equi': 'equilibiration',
        'prod': 'production'
                  }
    # loop iterating over each step that is to be performed
    for step in steps_list:
        # printing default parameters for the step
        def_params = default_parameters(step)
        print(f"For {steps_dict.get(step)}, default input file looks as follows:\n"
              f"{def_params}")
        # choice if user wants to change default parameters (more info on individual parameters will be provided when
        # user will consider changing them)
        USER_CHOICE_DEF_PARAMS = f"You might either stick to the default parameters, or change their individual values.\n" \
            f"Please keep in mind that not only each protein is different but also computational resources that are " \
            f"available to you may significantly differ from a standard HPC resource, for which this program was designed," \
            f" therefore you SHOULD consider every parameter carefully. Default values are rather a proposition, which" \
            f" will work correctly but are not likely to be optimal.\n" \
            f"Would you like to use default parameters that will control your {steps_dict.get(step)} run, or you'd" \
            f" rather change some of those values?\n" \
            f"- press 'y' if you want to use default parameters\n" \
            f"- press 'n' if you want to change parameters\n" \
            f"Please, provide your choice:\n"
        while True:
            try:
                user_input_def_params = str(input(USER_CHOICE_DEF_PARAMS).lower())
                if user_input_def_params == 'y':
                    # default parameters for this step will be used
                    break
                elif user_input_def_params == 'n':
                    # user wants to change parameters and here he will have the chance to do so
                    break
            except:
                print('Please, provide valid input')
        pass

    pass



amber_parameters_functions = [
    file_naming,
    clearing_control,
    qm_or_not,
    qm_parameters,
    steps_to_perform,
    md_parameters
]

methods_generator = (y for y in amber_parameters_functions)


def queue_methods():
    next(methods_generator, None)
    global stop_generator
    stop_generator = False
    for x in amber_parameters_functions:
        x()
        # if a condition is met, generator is stopped
        if stop_generator:
            # I do not know if this prompt is necessary
            print('\nProgram has not finished normally - it appears that something was wrong with your structure. \n'
                  'Apply changes and try again!\n')
            break