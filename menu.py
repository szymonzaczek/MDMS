import topology_preparation.topology_prep


print("Hello and welcome to Simple Amber (SAmber) created by Szymon Zaczek!\n"
      "This piece of software makes running Molecular Dynamics easy and straightforward, allowing non-experts "
      "in the field of computational chemistry to use Amber\n- one of the most renowned Molecular Dynamics packages available.\n"
      "If you use SAmber in your work, please, consider acknowledging my work by citing the original paper: xxx.\n"
      "If you have any suggestions, queries, bug reports or simply questions about how to proceed with your work using "
      "SAmber, please, contact me at: "
      "szymon.zaczek@edu.p.lodz.pl\n" )

USER_CHOICE_MENU = """\nPlease specify, what you would like to do:
• press 'p' for preparing topology and coordinate files for Amber - they are necessary for running MD calculations
• press 'i' for preparing Amber input files - they contain parameters for your simulations
• press 'r' for running simulations
• press 'q' in order to quit
Please, provide tour choice: """

def menu():
    while True:
        try:
            user_input_menu = str(input(USER_CHOICE_MENU)).lower()
            if user_input_menu == 'p':
                print('You will be guided on how to obtain topology and coordinate files for Amber. Buckle up!\n')
                topology_preparation.topology_prep.queue_methods()
                break
            elif user_input_menu == 'i':
                print('You will be guided through obtaining input files for Amber, which control your simulations. Buckle up!\n')
                break
            elif user_input_menu == 'r':
                print('You will be guided on how to run your simulations. Buckle up!\n')
                break
            elif user_input_menu == 'q':
                break
            else:
                raise Exception
        except Exception:
            print('Please, provide a valid input.')

menu()
