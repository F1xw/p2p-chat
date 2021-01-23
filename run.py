import sys
import importlib.util
import subprocess
import os

reqModules = ['socket', 'threading', 'curses', 'npyscreen', 'time', 'datetime', 'pyperclip'] # Array with required modules
missingModules = [] # Array to fill with missing modules

if sys.version_info < (3, 3): # Check the python version
    print("Python version 3.3 is required to run p2p-chat. Your version is {0}.".format(sys.version))
    exit(1)
else:
    for module in reqModules: # Go through each module and check if its installed
        if not module in sys.modules and importlib.util.find_spec(module) == None:
            missingModules.append(module)
            print("Required module not found: {0}".format(module))
        else:
            print("{0} is installed".format(module))

    if missingModules: # If there are any missing modules, try and install them | Installation requires pip
        print("At least one required module is missing. Exiting...")
        if "pip" in sys.modules or importlib.util.find_spec("pip") is not None:
            answ = input("Should we try and install missing modules with pip? [y/n] >> ")
            if answ == "y" or answ == "Y":
                for module in missingModules:
                    if module == "curses" and os.name == "nt":
                        print("Curses needs to be installed manually. See https//github.com/F1xw/p2p-chat#Requirements")
                        continue
                    try:
                        pip = subprocess.Popen([sys.executable, "-m", "pip", "install", module])
                        pip.wait()
                    except Exception:
                        pass
                    if not module in sys.modules and importlib.util.find_spec(module) == None:
                        print("Failed to install {0}.".format(module))
                    else:
                        print("Installed {0}.".format(module))
                        missingModules.remove(module)
    
if missingModules:
    print("Please try to install these modules manually:")
    for module in missingModules:
        print("-",module)
        i = input("Press Enter to Exit >>")
        exit(1)
else:
    import chat # Import the Chat App from chat.py
    chatApp = chat.ChatApp().run() # Run the Chat App



