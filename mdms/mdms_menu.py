#!/usr/bin/env python3
import mdms.initial_struc
import mdms.topology_prep
import mdms.run_simulations
import mdms.amber_parameters

print(
    "Hello and welcome to Molecular Dynamics Made Simple (MDMS) created by Szymon Zaczek!\n"
    "This piece of software makes running Molecular Dynamics easy and straightforward, allowing non-experts "
    "in the field of computational chemistry to use Amber\n- one of the most renowned Molecular Dynamics packages available.\n"
    "If you use MDMS in your work, please, consider acknowledging my work by citing the original paper: xxx.\n"
    "If you have any suggestions, queries, bug reports or simply questions about how to proceed with your work using "
    "MDMS, please, contact me at: "
    "szymon.zaczek@edu.p.lodz.pl\n")

USER_CHOICE_MENU = """\nPlease specify, what you would like to do:
- press 'p' for establishing the protein (or protein-ligand complex) initial structure
- press 't' for preparing topology and coordinate files for Amber, which are necessary for running MD simulations
- press 'i' for preparing Amber input files - they contain parameters for your simulations
- press 'r' for running simulations
- press 'q' in order to quit
Please, provide your choice: """


def menu():
    while True:
        try:
            user_input_menu = str(input(USER_CHOICE_MENU)).lower()
            if user_input_menu == 'p':
                print(
                    'You will be getting an initial structure for your system. Buckle up!\n')
                mdms.initial_struc.queue_methods()
                print(
                    'You have completed the first step required for running MD simulations. Congratulations!')
            elif user_input_menu == 't':
                print(
                    'You will obtain topology and coordinate files for Amber. Buckle up!\n')
                mdms.topology_prep.queue_methods()
                print(
                    'You have completed the next step required for running MD simulations. Congratulations')
            elif user_input_menu == 'i':
                print(
                    'You will be obtaining input files for Amber, which will control your simulations. Buckle up!\n')
                mdms.amber_parameters.queue_methods()
                print(
                    'You have managed to obtain input Amber input parameters. Get ready for starting your calculations!\n')
            elif user_input_menu == 'r':
                print('You will be guided on how to run your simulations. Buckle up!\n')
                mdms.run_simulations.queue_methods()
            elif user_input_menu == 'q' or user_input_menu == 'quit':
                print('Good luck with your endeavors and have a great day!')
                break
            else:
                print('Please, provide one of the available options.')
        except BaseException:
            print('Please, provide a valid input.')


menu()
