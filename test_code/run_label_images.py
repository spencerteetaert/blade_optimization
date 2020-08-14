import glob

from context import source
from source.label_images import main

while True:
    while True:
        image_folder = input("What folder are your images in? (copy and paste folder path)\n")

        temp = glob.glob(image_folder + "/*.*")
        print('\n')
        for i in range(0, len(temp)):
            print(temp[i])

        flag = input("Are the files from this folder (Y/N)?\n")
        if flag == "Y" or flag == "y":
            break
        else:
            print("Enter a new folder path.")

    data_type = "." + input("What type are your images? (JPG, PNG, JPEG, etc.)\n")

    output_folder = input("What folder do you want the results saved in?\n")

    flag = input("You've chosen:\n" + str(image_folder)+ "\nas your image folder,\n"+str(data_type,)+ "\nas your file extension, and\n"+\
        str(output_folder)+ "\nas your output location. Is this correct? (Y/N)\n")
    if flag == "Y" or flag == "y":
        break

main(image_folder=image_folder, data_type=data_type, output_folder=output_folder)