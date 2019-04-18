import subprocess
import os
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


#clear control?


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
                    f"queueing system on your machine\n." \
                    f"It should contain all of the information required for running simulations, such as nodes " \
                    f"specification, number of processors/cores per node used, wall-time, grant name, memory " \
                    f"specification etc.\n" \
                    f"If you need to load modules onto your computing nodes, this script should also contain this" \
                    f"information.\n" \
                    f"This script however, should not contain any Amber-specific content, since it will be added" \
                    f"just in the second." \
                    f"Please, provide path to the script:\n "
                while True:
                    try:
                        user_input_script_path = str(input(USER_CHOICE_SCRIPT_PATH))
                        if file_check(Path(user_input_script_queue)) == True:
                            # there is such a file and we are good
                            save_to_file(f"script = {user_input_script_queue}\n", filename)
                            break
                        elif file_check(Path(user_input_script_path)) == False:
                            print("There is no such file. Please, provide valid path to the file.")
                        break
                    except:
                        print('Please, provide valid input.')
                break
            elif user_input_queue_terminal == 't':
                # saving info to the control file
                save_to_file(f"run_type = terminal\n", filename)
                break
        except:
            print('Please, provide valid input')


run_functions = [
    file_naming,
]


methods_generator = (y for y in run_functions)


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