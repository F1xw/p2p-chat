import sys
import importlib.util
import subprocess

reqModules = ['socket', 'threading', 'curses', 'npyscreen', 'time', 'datetime', 'io']
missingModules = []
missing = 0

if sys.version_info < (3, 3):
    print("Python version 3.3 is required to run p2p-chat. Your version is {0}.".format(sys.version))
    exit(1)
else:
    for module in reqModules:
        if not module in sys.modules and importlib.util.find_spec(module) == None:
            missing += 1
            missingModules.append(module)
            print("Required module not found: {0}".format(module))
        else:
            print("{0} is installed".format(module))

    if missing > 0:
        print("At least one required module is missing. Exiting...")
        if "pip" in sys.modules or importlib.util.find_spec("pip") is not None:
            answ = input("Should we try and install missing modules with pip? [y/n] >> ")
            if answ == "y" or answ == "Y":
                for module in missingModules:
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                    except Exception:
                        pass
                    if not module in sys.modules and importlib.util.find_spec(module) == None:
                        print("Failed to install {0}.".format(module))
                    else:
                        print("Installed {0}.".format(module))
                        missing -= 1
                        missingModules.remove(module)
                if missingModules == 0:
                    print("All modules have been installed.")
                else:
                    print("At least one installation failed. Please try to install these modules manually:")
                    for module in missingModules:
                        print(module)
                    exit(1)
            else:
                print("Please try to install these modules manually:")
                for module in missingModules:
                    print(module)
                    exit(1)     
        else:
            print("Please try to install these modules manually:")
            for module in missingModules:
                print(module)
                exit(1)
    

import chat
chatApp = chat.ChatApp().run()



