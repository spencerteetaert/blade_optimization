import glob

from context import source
from source.process_data import main

while True:
    DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\Program Data\GOOD.csv"
    data_folder = input("What folder is your labelled data located in? (copy and paste folder path)\n")

    file_name = input("What is the name of your labelled data? (include file extension)\n")

    f = data_folder + "\\" + file_name

    flag = input("You've chosen:\n" + f + "\nas your data location, is this correct? (Y/N)\n")
    if flag == "Y" or flag == "y":
        try:
            t = open(f)
            t.close()
            break
        except:
            print("File unable to be opened. Please try again")

main(data_path=f)