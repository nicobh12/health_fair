import os, platform
def clear_console():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
