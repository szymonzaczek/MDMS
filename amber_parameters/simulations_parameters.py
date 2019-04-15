import re

def parameters():
    # here there is info store about individual parameters
    parameters_dict = {
        'imin': 'defining minimization (imin = 0) or dynamics (imin = 1)',
        'irest': 'defining if simulations is restarted (irest = 0) or not (irest = 1)',
        'ntx': 'defining a way in which coordinates are read',
        'ntb': 'periodic box defintion - constant volume (ntb = 1) or constant pressure (ntb = 2)',
        'cut': 'cutoff radius for nonbonded interactions in Angstroms, 8 is usually a good value',
        'ntc': 'SHAKE algorithm - if turned on (ntc = 2) hydrogen bonds are restrained',
        'ntf': 'force evaluation, if SHAKE is turned on, bond interactions involving H should be omitted (ntf = 2)',
    }
    pass