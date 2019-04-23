import subprocess
import os
import re
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
        'run_type',
        'program',
        'parallelism',
        'script',
        'command',
        'nr_processors'
    ]
    # writing content of control file without parameters in parameters list to
    # the temporary file
    with open(f"{filename}") as oldfile, open(filetemp, 'w') as newfile:
        for line in oldfile:
            if not any(parameters in line for parameters in parameters):
                newfile.write(line)
    # replacing control file with temporary file
    os.replace(filetemp, filename)


def queue_or_terminal():
    USER_CHOICE_QUEUE_TERMINAL = f"Would you like to perform your simulations by submitting job to the queue, or " \
        f"rather you'd run it directly in your terminal?\n" \
        f"Please note that if you are using HPC clusters, you should most likely submit your jobs to the queue." \
        f" This is due to the fact that HPC clusters tend to have login nodes and computing nodes separated, " \
        f"which maximizes performance.\n" \
        f"If you are using your own computer, you should most likely just run your jobs in the terminal\n" \
        f"How would you like to run your simulations?\n" \
        f"- press 'q' if you want to submit your simulations to the queue\n" \
        f"- press 't' if you want to run your simulations directly in the terminal\n" \
        f"Please, provide your choice:\n"
    while True:
        try:
            user_input_queue_terminal = str(input(USER_CHOICE_QUEUE_TERMINAL).lower())
            if user_input_queue_terminal == 'q':
                # saving info to the control file
                save_to_file(f"run_type = queue\n", filename)
                # prompt for providing script for running jobs
                USER_CHOICE_SCRIPT_PATH = f"Please, provide path to the sample script which works correctly with" \
                    f" queueing system on your machine.\n" \
                    f"It should contain all of the information required for running simulations, such as nodes " \
                    f"specification, number of processors/cores per node used, wall-time, grant name, memory " \
                    f"specification etc.\n" \
                    f"If you need to load modules onto your computing nodes, this script should also contain this" \
                    f" information.\n" \
                    f"This script however, should not contain any Amber-specific content, since it will be added" \
                    f" just in the second.\n" \
                    f"Please, provide path to the script:\n"
                while True:
                    try:
                        user_input_script_path = str(input(USER_CHOICE_SCRIPT_PATH))
                        if file_check(Path(user_input_script_path)) == True:
                            # there is such a file and we are good
                            save_to_file(f"queue_script = {user_input_script_path}\n", filename)
                            break
                        elif file_check(Path(user_input_script_path)) == False:
                            print("There is no such file. Please, provide valid path to the file.")
                            break
                    except:
                        print('Please, provide valid input.')
                # command for executing script
                USER_CHOICE_COMMAND = f"Please, provide the command that is used to submit a job to be executed in " \
                    f"the queueing system on your machine (it can be qsub, sbatch, etc.):\n"
                while True:
                    try:
                        user_input_command = str(input(USER_CHOICE_COMMAND))
                        save_to_file(f"command = {user_input_command}\n", filename)
                        break
                    except:
                        print('Please, provide valid input')
                break
            elif user_input_queue_terminal == 't':
                # saving info to the control file
                save_to_file(f"run_type = terminal\n", filename)
                break
        except:
            print('Please, provide valid input')


def sander_or_pmemd():
    # sander or pmemd choice
    USER_CHOICE_PROGRAM = f"Within Amber, there are 2 programs for running MD simulations: Sander and PMEMD.\n" \
        f"Sander is distributed along with Ambertools and is free to use.\n" \
        f"PMEMD offers improved performance over Sander, though its functionality is slightly limited. Nonetheless," \
        f" if you want to perform regular MD simulations, PMEMD will most likely be the better choice, though" \
        f"it must obviously be available to you at your current machine.\n" \
        f"- press 's' for using Sander\n" \
        f"- press 'p' for using PMEMD\n" \
        f"Please, provide your choice:\n"
    while True:
        try:
            user_input_program = str(input(USER_CHOICE_PROGRAM).lower())
            # break only if input is 's' or 'p'
            if user_input_program == 's':
                save_to_file(f"program = sander\n", filename)
                break
            elif user_input_program == 'p':
                save_to_file(f"program = pmemd\n", filename)
                break
        except:
            print('Please, provide valid input.')


def serial_or_parallel():
    # reading info about sander or pmemd choice
    control = read_file(filename)
    engine = r'program\s*=\s*(.*)'
    engine_match = re.search(engine, control).group(1)
    # finding what run do we proceed with
    run_type = r'run_type\s*=\s*(.*)'
    run_type_match = re.search(run_type, control).group(1)
    USER_CHOICE_PARALLELISM = f"For your simulations you might either use serial or parallel {run_type_match} code.\n" \
        f"Parallel code allow using multiple processors for a single simulation thus finishing faster. It requires" \
        f" parallel version of {engine_match} though.\n" \
        f"If it is available, parallel version is preferable.\n" \
        f"- press 's' for using serial code of {engine_match}\n" \
        f"- press 'p' for using parallel code of {engine_match}\n" \
        f"Please, provide your choice:\n"
    while True:
        try:
            user_input_parallelism = str(input(USER_CHOICE_PARALLELISM).lower())
            if user_input_parallelism == 's':
                save_to_file(f"parallelism = serial\n", filename)
                break
            elif user_input_parallelism == 'p':
                USER_CHOICE_PROCESSORS = f"Please choose number of processors that will be used for running your job.\n" \
                    f"If you are using queueing system for submitting your job, please note, that the number provided" \
                    f" here must be consistent with what is specified in the queue script provided before.\n" \
                    f"Please, provide your choice:\n"
                user_input_processors = input(USER_CHOICE_PROCESSORS)
                # check if it can be changed to int; if it can't it will be halted
                int_user_input_processors = int(user_input_processors)
                # saving is at the end since otherwise multiple parallelism might have been saved
                save_to_file(f"parallelism = parallel\n", filename)
                save_to_file(f"nr_processors = {user_input_processors}\n", filename)
                break
        except:
            print('Please, provide valid input')


def running_simulations():
    # establishing name of the job - job will be name job_top_name
    control = read_file(filename)
    top_name = r'top_name\s*=\s*(.*)'
    top_name_match = re.search(top_name, control).group(1)
    job_name = f"job_{top_name_match}"
    # removing job file if it exists
    if file_check(Path(f"{job_name}")):
        os.remove(Path(f"{job_name}"))
    print(f"\nFile that will be executed on the machine will be named: {job_name}\n")
    # finding which engine will be run
    engine = r'program\s*=\s*(.*)'
    engine_match = re.search(engine, control).group(1)
    # reading steps
    steps = r'procedure.*=.*\[(.*)\]'
    steps_match = re.search(steps, control).group(1)
    # removing quotes from string
    steps_string = steps_match.replace("'", "")
    # removing whitespaces and turning string into a list
    steps_list = re.sub(r'\s', '', steps_string).split(',')
    # finding individual input files for each step
    steps_input_list = []
    for step in steps_list:
        entry = f"{step}\s*=\s*(.*)"
        entry_match = re.search(entry, control).group(1)
        steps_input_list.append(entry_match)
    # finding parallelism of a job
    parallelism = r'parallelism\s*=\s*(.*)'
    parallelism_match = re.search(parallelism, control).group(1)
    if parallelism_match == 'parallel':
        nr_processors = r"nr_processors\s*=\s*(.*)"
        nr_processors_match = re.search(nr_processors, control).group(1)
    # finding what run do we proceed with
    run_type = r'run_type\s*=\s*(.*)'
    run_type_match = re.search(run_type, control).group(1)
    if run_type_match == 'queue':
        # finding script for queueing system
        queue_script = r'queue_script\s*=\s*(.*)'
        queue_script_match = re.search(queue_script, control).group(1)
        # finding command for submitting job to queueing system
        command = r'command\s*=\s*(.*)'
        command_match = re.search(command, control).group(1)
        # if simulations are parallel, execute this
        if parallelism_match == 'parallel':
            with open(job_name, 'w') as file:
                file.write(read_file(queue_script_match))
                for x in range(0, len(steps_list)):
                    # first execution of script requires inpcrd, further ones requires coordinates from previous step
                    if x == 0:
                        file.write(f"\nmpirun -np {nr_processors_match} {engine_match}.MPI -O -i {steps_input_list[x]} -o {steps_list[x]}.out -c {top_name_match}.inpcrd "
                           f"-p {top_name_match}.prmtop -r {steps_list[x]}.ncrst -inf {steps_list[x]}.mdinfo")
                    else:
                        file.write(f"\nmpirun -np {nr_processors_match} {engine_match}.MPI -O -i {steps_input_list[x]} -o {steps_list[x]}.out -c {steps_list[x-1]}.ncrst "
                           f"-p {top_name_match}.prmtop -r {steps_list[x]}.ncrst -inf {steps_list[x]}.mdinfo")
        elif parallelism_match == 'single':
            # HERE I STOPPED
            pass
        pass
    elif run_type_match == 'terminal':
        pass
    pass


run_functions = [
    file_naming,
    clearing_control,
    queue_or_terminal,
    sander_or_pmemd,
    serial_or_parallel,
    running_simulations
]


methods_generator = (y for y in run_functions)


def queue_methods():
    next(methods_generator, None)
    global stop_generator
    stop_generator = False
    for x in run_functions:
        x()
        # if a condition is met, generator is stopped
        if stop_generator:
            # I do not know if this prompt is necessary
            print('\nProgram has not finished normally - it appears that something was wrong with your structure. \n'
                  'Apply changes and try again!\n')
            break