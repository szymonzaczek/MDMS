import os
import re
import readline
from pathlib import Path

# allowing tab completion of files' paths
readline.parse_and_bind("tab: complete")

def file_naming():
    # getting name for a control file, which will contain all info
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
        'procedure',
        'min',
        'heat',
        'equi',
        'prod'
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
    # asking user if he wants to perform QM/MM calculations
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
    # reading control file
    control = read_file(filename)
    # reading if qm was chosen or not
    qm = r'qm\s*=\s*(.*)'
    qm_match = re.search(qm, control)
    # set ifqnt val to 0; if qm was specified, change its value to 1
    ifqnt_val = 0
    if qm_match:
        ifqnt_val = 1
    # defining def_params
    def_params = ""
    if step == 'min':
        def_params = """{step}
&cntrl
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
 ifqnt={ifqnt}
/

""".format(ifqnt=ifqnt_val, step=step)
    elif step == 'heat':
        def_params = """{step}
&cntrl
 imin = 0,
 irest = 0,
 ntx = 1,
 ntb = 1,
 ntp = 0,
 cut = 8.0,
 ntc = 2,
 ntf = 2,
 tempi = 0.0,
 temp0 = 300.0,
 ntt = 3,
 gamma_ln = 2.0,
 nstlim = 25000,
 dt = 0.002,
 ntpr = 100,
 ntwx = 500,
 ntwr = 5000,
 ig=-1,
 ifqnt={ifqnt},
 nmropt=1,
/
&wt type='TEMP0', istep1=0, istep2=25000, value1=0.0, value2=300.0 /
&wt type='END' /

""".format(ifqnt=ifqnt_val, step=step)
    elif step == 'equi':
        def_params = """{step}
&cntrl
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
 nstlim = 75000,
 dt = 0.002,
 ntpr = 500,
 ntwx = 500,
 ntwr = 5000,
 ig=-1,
 ifqnt={ifqnt},
 nmropt=0
/

""".format(ifqnt=ifqnt_val, step=step)
    elif step == 'prod':
        def_params = """{step}
&cntrl
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
 ntwr = 20000,
 ig=-1,
 ifqnt={ifqnt},
 nmropt=0
/

""".format(ifqnt=ifqnt_val, step=step)
    return def_params


def qm_parameters():
    # reading from control file if there is a qm part and then choose parameters for qm
    # reading control file
    control = read_file(filename)
    # reading if qm was chosen or not
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
                    USER_CHOICE_QMPATH = f"\nPlease, provide path to the file that contains parameters for the QM part" \
                        f" for your simulations (it should only contain &qmmm namelist):\n"
                    while True:
                        try:
                            user_input_qmpath = str(input(USER_CHOICE_QMPATH))
                            print(Path(user_input_qmpath))
                            if file_check(Path(user_input_qmpath)) == True:
                                # everything is good an we may close the loop
                                save_to_file(f"qm_control = {user_input_qmpath}\n", filename)
                                break
                            elif file_check(Path(user_input_qmpath)) == False:
                                # there is no file with provided path and user is prompted to provide path again
                                print('There is no such file. Please, provide a valid path')
                        except:
                            print('Please, provide a valid input')
                    break
                elif user_input_qmcontrol == 'n':
                    # defining qmatoms
                    USER_CHOICE_QMATOMS = f"\nWhich atoms from your system should be treated with QM methods? Any valid " \
                        f"Amber mask will work (for more info about masks refer to Amber manual).\n" \
                        f"Please, provide your choice (Amber mask formatting is required):\n"
                    while True:
                        try:
                            user_input_qmatoms = str(input(USER_CHOICE_QMATOMS).upper())
                            break
                        except:
                            print('Please, provide valid input')
                    # defining spin
                    USER_CHOICE_QMSPIN = f"\nWhat is the spin of the QM part of your system?\n" \
                        f"Please, provide spin value for the QM part of your system (positive integer value):\n"
                    while True:
                        try:
                            user_input_qmspin = int(input(USER_CHOICE_QMSPIN))
                            if user_input_qmspin > 0:
                                break
                        except:
                            print('Please, provide valid input')
                    # defining charge
                    USER_CHOICE_QMCHARGE = f"\nWhat is the charge of the QM part of your system?\n" \
                        f"Please, provide charge value for the QM part of your system (integer value):\n"
                    while True:
                        try:
                            user_input_qmcharge = int(input(USER_CHOICE_QMCHARGE))
                            break
                        except:
                            print('Please, provide valid input')
                    # define qmmethod
                    USER_CHOICE_QMMETHOD = f"\nWhich QM method would you like to use? The following options are available:\n" \
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
                    # content of a qmmm namelist
                    qm_content = (f"&qmmm\n"
                                   f" qmmask = '{user_input_qmatoms}',\n"
                                   f" spin = {user_input_qmspin},\n"
                                   f" qmcharge = {user_input_qmcharge},\n"
                                   f" qmshake = 0,\n"
                                   f" qm_ewald = 1,\n"
                                   f" qm_pme = 1,\n"
                                   f" qm_theory = '{user_input_qmmethod}',\n"
                                   f" printcharges = 1,\n"
                                   f" writepdb = 1,\n"
                                   f"/"
                                   f"")
                    # turning qm_content this into a list and into a dictionary
                    parameters_list = []
                    parameters_dict = {}
                    for line in qm_content.splitlines():
                        # removing white spaces
                        line = re.sub(r'\s', '', line)
                        # removing commas
                        line = re.sub(r'\,', '', line)
                        # getting list of two elements for a single line (parameter and its value)
                        parameter_value = line.split('=')
                        # if qmmmm line or the last line is considered this is skipped
                        not_parameters_list = ['&qmmm', '/', '']
                        if parameter_value[0] in not_parameters_list:
                            continue
                        # storing parameters in a list
                        parameters_list.append(parameter_value[0])
                        # storing parameters in a dict
                        parameters_dict.update({parameter_value[0]: parameter_value[1]})
                        # THIS MIGHT NOT BE USEFUL - NICELY FORMATTED STRING IS ALREADY AVAILABLE IN qm_content
                        """
                        parameters_values_string = str(parameters_dict)
                        # formatting outputs so it will be perfect
                        parameters_values_string = re.sub(r'\'', '', parameters_values_string)
                        parameters_values_string = re.sub(r'\s', '', parameters_values_string)
                        parameters_values_string = re.sub(r'\:', ' = ', parameters_values_string)
                        parameters_values_string = re.sub(r'\,', ',\n', parameters_values_string)
                        parameters_values_string = re.sub(r'\{', '&cntrl\n', parameters_values_string)
                        parameters_values_string = re.sub(r'\}', '\n/\n', parameters_values_string)
                        """
                    print(f"\nCurrently, QM/MM parameters look as follows:\n"
                          f"{qm_content}\n")
                    USER_CHOICE_CHANGE_PARAMS = f"You might either change QM/MM parameters or stick to their current" \
                        f"values. Please note, that you will also be able to add additional parameters that were not" \
                        f" considered before, if you find them useful.\n" \
                        f"Would you like to retain current QM/MM parameters?\n" \
                        f"- press 'y' if you want to use current QM/MM parameters values\n" \
                        f"- press 'n' if you want to change (or add) current QM/MM parameters\n" \
                        f"Please, provide your choice:\n"
                    try:
                        user_input_change_params = str(input(USER_CHOICE_CHANGE_PARAMS).lower())
                        if user_input_change_params == 'y':
                            # user do not want to change qmmm, so loop breaks
                            break
                        elif user_input_change_params == 'n':
                            # changing qmmm parameters
                            USER_CHOICE_PARAMS = f"\nThere are following parameters defined for the QM/MM part of" \
                                f"your system:\n" \
                                f"{parameters_list}\n" \
                                f"Would you like to change of the parameters or add another one?\n" \
                                f"- type 'parameter_code' (for instance 'printcharges' in order to change its value\n" \
                                f"- type 'a' in order to add additional parameter\n" \
                                f"- type 'q' if you want to stop modifying QM/MM parameters\n" \
                                f"Please, provide your choice:\n"
                            while True:
                                try:
                                    user_input_params = str(input(USER_CHOICE_PARAMS).lower())
                                    if user_input_params == 'a':
                                        # adding new parameter to QM/MM
                                    elif user_input_params in parameters_list:
                                        # if its true, just update parameter value
                                    elif user_input_params == 'q':
                                        # quitting changing parameters and saving current values
                                    pass
                                except:
                                    pass
                            pass
                    except:
                        pass

                    qm_input = 'qm_control.in'

                    # if qm_input already exist, remove it
                    if file_check(Path(qm_input)):
                        os.remove(Path(qm_input))
                    # save qm info to qm_input
                    with open(qm_input, 'w') as file:
                        file.write(qm_content)
                    save_to_file(f"qm_control = {qm_input}\n", filename)
                    break
            except:
                print('Please, provide valid input')


def md_parameters():
    # here there is info store about individual parameters
    parameters_dict = {
        'imin': 'defining minimization (imin = 0) or dynamics (imin = 1)',
        'irest': 'defining if simulations is restarted (irest = 0) or not (irest = 1)',
        'ntx': 'defining a way in which coordinates are read',
        'ntb': 'periodic box definition - constant volume (ntb = 1) or constant pressure (ntb = 2)',
        'cut': 'cutoff radius for nonbonded interactions in Angstroms, 8 is usually a good value',
        'ntc': 'SHAKE algorithm - if turned on (ntc = 2) hydrogen bonds are restrained',
        'ntf': 'force evaluation, if SHAKE is turned on, bond interactions involving H should be omitted (ntf = 2)',
        'tempi': 'initial temperature',
        'temp0': 'target temperature',
        'ntt': 'thermostat type, Langevin Dynamics is defined as ntt = 3 and is probably the best choice',
        'gamma_ln': 'collision frequency, should be between 2.0 and 5.0',
        'nstlim': 'number of MD steps to be performed',
        'dt': 'timestep value (in ps), with SHAKE turned on 0.002 is the max reasonable value',
        'ntpr': 'print the energy information every n-th steps',
        'ntwx': 'saves coordinates every n-th steps',
        'ntwr': 'saves restart files every n-th steps',
        'ig': 'setting random seed',
        'ifqnt': 'turning on QM/MM (ifqnt = 1) or not (ifqnt = 0)',
        'nmropt': 'turning NMR restraints on (nmropt = 1), could be also used for controlling temperature',
        'maxcyc': 'maximum number of minimization steps',
        'ncyc': 'after n-steps, change to conjugate gradient optimization instead of steepest descent'
    }
    # reading info from control file
    control = read_file(filename)
    steps = r'procedure\s*=\s*\[(.*)\]'
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
        # if the only step is production, default files require changes
        if steps_list == ['prod']:
            parameters_list = []
            # dictionary containing parameters and its values
            parameters_values_dict = {}
            # printing parameters that are in the default file for the current step
            for line in def_params.splitlines():
                # changing string to the desired format
                # removing whitespaces
                line = re.sub(r'\s', '', line)
                # removing commas in string
                line = re.sub(r'\,', '', line)
                # getting list of two elements for a single line (parameter and its default value
                parameter_value = line.split('=')
                # if cntrl line, title line or the last line is considered, this is skipped
                not_parameters_list = ['&cntrl', '/', 'min', 'heat', 'equi', 'prod', '']
                if parameter_value[0] in not_parameters_list:
                    continue
                # storing parameters in a list
                parameters_list.append(parameter_value[0])
                # storing parameters and their values in a dictionary
                parameters_values_dict.update({parameter_value[0]: parameter_value[1]})
            # changing irest and ntx value if list has only prod value
            parameters_values_dict.update({'irest': '0'})
            parameters_values_dict.update({'ntx': '1'})
            # quitting changing parameters - saving all of the current values
            # converting dictionary with parameters to string
            parameters_values_string = str(parameters_values_dict)
            # formatting outputs so it will be perfect
            parameters_values_string = re.sub(r'\'', '', parameters_values_string)
            parameters_values_string = re.sub(r'\s', '', parameters_values_string)
            parameters_values_string = re.sub(r'\:', ' = ', parameters_values_string)
            parameters_values_string = re.sub(r'\,', ',\n', parameters_values_string)
            parameters_values_string = re.sub(r'\{', '&cntrl\n', parameters_values_string)
            parameters_values_string = re.sub(r'\}', '\n/\n', parameters_values_string)
            # in order to add spaces to the beginning of a string, at first a list will be created, which
            # later on will be joined to create properly formatted string
            parameters_values_list = []
            for line in parameters_values_string.splitlines():
                if line in not_parameters_list:
                    parameters_values_list.append(line)
                else:
                    line = ' ' + line
                    parameters_values_list.append(line)
            parameters_values_string = '\n'.join(parameters_values_list)
            def_params = (f"{step}\n" + parameters_values_string + "\n")
        print(f"For {steps_dict.get(step)}, default input file looks as follows:\n"
              f"{def_params}")
        # choice if user wants to change default parameters (more info on individual parameters will be provided when
        # user will consider changing them)
        USER_CHOICE_DEF_PARAMS = f"You might either stick to the default parameters, or change their individual values.\n" \
            f"Please keep in mind that not only each protein is different but also computational resources that are " \
            f"available to you may significantly differ from a standard HPC resource, for which this program was designed," \
            f" therefore you SHOULD consider every parameter carefully. Default values are rather a proposition, which" \
            f" will work correctly but are not likely to be optimal for your case.\n" \
            f"Would you like to use default parameters that will control your {steps_dict.get(step)} run, or you'd" \
            f" rather change some of those values?\n" \
            f"- press 'y' if you want to use default parameters\n" \
            f"- press 'n' if you want to change parameters (as well as perform QM/MM simulations)\n" \
            f"Please, provide your choice:\n"
        while True:
            try:
                user_input_def_params = str(input(USER_CHOICE_DEF_PARAMS).lower())
                # if prod is the only content of a list, ntx and irest values must be changed, therefore they are handled
                # in else clause
                if user_input_def_params == 'y':
                    # default parameters for this step will be saved to the file
                    file_step = def_params
                    break
                elif user_input_def_params == 'n':
                    # user wants to change parameters and here he will have the chance to do so
                    # list containing parameters for this step
                    parameters_list = []
                    # dictionary containing parameters and its values
                    parameters_values_dict = {}
                    # printing parameters that are in the default file for the current step
                    for line in def_params.splitlines():
                        # changing string to the desired format
                        # removing whitespaces
                        line = re.sub(r'\s', '', line)
                        # removing commas in string
                        line = re.sub(r'\,', '', line)
                        # getting list of two elements for a single line (parameter and its default value
                        parameter_value = line.split('=')
                        # if cntrl line, title line or the last line is considered, this is skipped
                        not_parameters_list = ['&cntrl', '/', 'min', 'heat', 'equi', 'prod', '']
                        if parameter_value[0] in not_parameters_list:
                            continue
                        # storing parameters in a list
                        parameters_list.append(parameter_value[0])
                        # storing parameters and their values in a dictionary
                        parameters_values_dict.update({parameter_value[0]: parameter_value[1]})
                    if step == 'equi':
                        print(f"\n!!WARNING!!\n"
                              f"If you want to choose the rate at which system is heated (what is controlled with "
                              f"&wt type='TEMP0' statement) you need to perform it manually in the file controlling"
                              f" {steps_dict.get(step)} step, prior to running your simulations.\n"
                              f"Ideally, you will heat your system for as long as heating steps is happening and then"
                              f" proceed with equilibration.\n")
                    # prompt which parameters user would like to change
                    USER_CHOICE_PARAMS = f"\nThere are following parameters defined for {steps_dict.get(step)}:\n" \
                        f"{parameters_list}\n" \
                        f"Would you like to change one of them, add another parameter to this list or perhaps" \
                        f" you would like to carry out QM/MM calculations?\n" \
                        f"- type 'parameter_code' (for instance 'cut') in order to change its value\n" \
                        f"- type 'a' in order to add additional parameter\n" \
                        f"- type 'q' if you want to stop modifying parameters for {steps_dict.get(step)} step.\n" \
                        f"Please, provide your choice:\n"
                    if steps_list == ['prod']:
                        # changing irest and ntx value if list has only prod value
                        parameters_values_dict.update({'irest': '0'})
                        parameters_values_dict.update({'ntx': '1'})
                        # from here on it might not be useful
                        """# quitting changing parameters - saving all of the current values
                        # converting dictionary with parameters to string
                        parameters_values_string = str(parameters_values_dict)
                        # formatting outputs so it will be perfect
                        parameters_values_string = re.sub(r'\'', '', parameters_values_string)
                        parameters_values_string = re.sub(r'\s', '', parameters_values_string)
                        parameters_values_string = re.sub(r'\:', ' = ', parameters_values_string)
                        parameters_values_string = re.sub(r'\,', ',\n', parameters_values_string)
                        parameters_values_string = re.sub(r'\{', '&cntrl\n', parameters_values_string)
                        parameters_values_string = re.sub(r'\}', '\n/\n', parameters_values_string)
                        # in order to add spaces to the beginning of a string, at first a list will be created, which
                        # later on will be joined to create properly formatted string
                        parameters_values_list = []
                        for line in parameters_values_string.splitlines():
                            if line in not_parameters_list:
                                parameters_values_list.append(line)
                            else:
                                line = ' ' + line
                                parameters_values_list.append(line)
                        parameters_values_string = '\n'.join(parameters_values_list)
                        file_step = (f"{step}\n" + parameters_values_string)"""
                        # until here it might not be useful
                    while True:
                        try:
                            user_input_params = str(input(USER_CHOICE_PARAMS).lower())
                            # if input is in parameters list, print this parameter value with info what it is doing
                            if user_input_params == 'a':
                                # adding additional parameters to the current step
                                USER_CHOICE_ADD_PARAM = (f"\n!!WARNING!!\n" \
                                    f"You chose to provide additional parameters for {steps_dict.get(step)} step.\n" \
                                    f"Keep in mind, that those parameters MUST be valid Amber parameters (see Manual " \
                                    f"for detailed information).\n" \
                                    f"The parameters that you will introduce MUST be consistent " \
                                    f"with other parameters from {steps_dict.get(step)} step - for instance, you cannot" \
                                    f" specify implicit solvation, if there are periodic boundary conditions applied." \
                                    f" Otherwise, your simulation will not start due to Amber error.\n" \
                                    f"Keep also in mind, that MDMS is not capable of checking validity of those " \
                                    f"parameters - you will be notified that something is wrong when you will begin " \
                                    f"running your simulations.\n" \
                                    f"Please, provide name of the parameter that you would like to introduce:\n")
                                while True:
                                    try:
                                        # providing name of the additional parameter
                                        user_input_add_param = str(input(USER_CHOICE_ADD_PARAM).lower())
                                        USER_CHOICE_ADD_PARAM_VALUE = (
                                            f"Please, provide value for the {user_input_add_param} parameter:\n")
                                        user_input_add_param_val = str(input(USER_CHOICE_ADD_PARAM_VALUE))
                                        # check if it can be changed to float; if yes, it must
                                        # be numerical value and can be put into dictionary, otherwise it is halted
                                        user_input_add_param_val_float = float(user_input_add_param_val)
                                        # saving new params into a dictionary
                                        parameters_values_dict.update({user_input_add_param: user_input_add_param_val})
                                        break
                                    except:
                                        print('Please, provide valid input.')
                            elif user_input_params == 'q':
                                # quitting changing parameters - saving all of the current values
                                # converting dictionary with parameters to string
                                parameters_values_string = str(parameters_values_dict)
                                # formatting outputs so it will be perfect
                                parameters_values_string = re.sub(r'\'', '', parameters_values_string)
                                parameters_values_string = re.sub(r'\s', '', parameters_values_string)
                                parameters_values_string = re.sub(r'\:', ' = ', parameters_values_string)
                                parameters_values_string = re.sub(r'\,', ',\n', parameters_values_string)
                                parameters_values_string = re.sub(r'\{', '&cntrl\n', parameters_values_string)
                                parameters_values_string = re.sub(r'\}', '\n/\n', parameters_values_string)
                                # adding title to the input file
                                file_step = (f"{step}\n" + parameters_values_string)
                                #file_step = parameters_values_string
                                parameters_values_list = []
                                for line in parameters_values_string.splitlines():
                                    if line in not_parameters_list:
                                        parameters_values_list.append(line)
                                    else:
                                        line = ' ' + line
                                        parameters_values_list.append(line)
                                parameters_values_string = '\n'.join(parameters_values_list)
                                file_step = (f"{step}\n" + parameters_values_string + '\n')
                                break
                            elif user_input_params in parameters_list:
                                print(parameters_values_dict)
                                USER_CHOICE_PARAM_VALUE = f"\nYou chose to change value of the '{user_input_params}' parameter.\n" \
                                    f"This parameter does the following job:\n" \
                                    f"{parameters_dict.get(user_input_params)}\n" \
                                    f"Its current value is set to:\n" \
                                    f"{parameters_values_dict.get(user_input_params)}\n" \
                                    f"What value would you like to use for your simulations? Please, provide your choice:\n"
                                while True:
                                    try:
                                        user_input_param_value = (input(USER_CHOICE_PARAM_VALUE))
                                        # if user inputs 0, just put it into the dictionary
                                        if user_input_param_value == '0':
                                            parameters_values_dict.update({user_input_params: user_input_param_value})
                                            break
                                        # check if it can be changed to float; if yes, it must
                                        # be numerical value and can be put into dictionary, otherwise halt
                                        else:
                                            input_float = float(user_input_param_value)
                                            parameters_values_dict.update({user_input_params: user_input_param_value})
                                            break
                                    except ValueError:
                                        print('Please, provide correct (numerical) value for this parameter')
                        except:
                            pass
                    break
            except:
                print('Please, provide valid input')
        # checking if step.in file exists - if yes it is deleted
        if file_check(Path(f"{step}.in")):
            os.remove(Path(f"{step}.in"))
        # save parameters for the current step to the input file
        with open(f"{step}.in", 'w') as file:
            file.write(file_step)
        # saving info into control file
        save_to_file(f"{step} = {step}.in\n", filename)



def qm_md_merging():
    # if there is qm, merge md and qm files
    # reading control file
    control = read_file(filename)
    # reading if qm was chosen or not
    qm = r'qm\s*=\s*(.*)'
    qm_match = re.search(qm, control)
    # if QM/MM was chosen, ask about parameters
    if qm_match:
        qm_match = qm_match.group(1)
        # reading steps
        steps = r'procedure.*=.*\[(.*)\]'
        steps_match = re.search(steps, control).group(1)
        # removing quotes from string
        steps_string = steps_match.replace("'", "")
        # removing whitespaces and turning string into a list
        steps_list = re.sub(r'\s', '', steps_string).split(',')
        prompt_qm = f"\nNOTE\n" \
            f"Right now, qm_qontrol file will be appended to all of the files that contain parameters for your " \
            f"simulations.\n"
        print(prompt_qm)
        for step in steps_list:
            # read qm_control.inp
            qm_control_pattern = r'qm_control\s*=\s*(.*)'
            qm_control_match = re.search(qm_control_pattern, control).group(1)
            qm_control = read_file(qm_control_match)
            # append qm_control to step.in
            with open(f"{step}.in", 'a') as file:
                file.write(qm_control)


amber_parameters_functions = [
    file_naming,
    clearing_control,
    steps_to_perform,
    qm_or_not,
    qm_parameters,
    md_parameters,
    qm_md_merging
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
