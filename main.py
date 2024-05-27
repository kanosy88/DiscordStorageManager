import os
from modules.GetFile import main_getfile
from modules.SendFile import main_sendFile

def main():
    os.system('cls')
    print("Action list:\n\n1) Send files\n2) Download a file")

    action = input("\nChoose an action: ")

    if int(action) == 1:
        main_sendFile()
    elif int(action) == 2:
        main_getfile()
    else:
        print(f"{action} is not an Action")
    
if __name__ == "__main__":
    main()
    input("\nPress enter to exit")