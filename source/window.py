import tkinter as tk
from tkinter import filedialog

from page import *

#Styles 
H1 = {"font":("Arial", 12, "bold"), "padx":20, "pady":10}
H2 = {"font":("Arial", 10, "bold"), "padx":15, "pady":7}
H3 = {"font":("Arial", 8, "bold"), "padx":10, "pady":5}
P1 = {"font":("Arial", 8), "padx":5, "pady":5}
P2 = {"font":("Arial", 8, "italic"), "padx":5, "pady":5}

#Main window construction 
window = tk.Tk()
window.geometry('500x500')
window.resizable(width=False, height=False)
window.title("Blade Design for Dummies")

# Page Initialization 
p1 = Page("Blade Design for Dummies", window)
p2 = Page("Label Images", window, p1)
p3 = Page("Label Images", window, p2)


#Page Functions
image_folder = tk.StringVar(p2.frame)
output_folder = tk.StringVar(p2.frame)
image_type = tk.StringVar(p2.frame)

def select_input_folder():
    global image_folder
    temp = tk.filedialog.askdirectory()
    image_folder.set(temp)
def select_output_folder():
    global output_folder
    temp = tk.filedialog.askdirectory()
    output_folder.set(temp)



# Landing page construction 
lbl = tk.Label(p1.frame, text="What would you like to do today?")
p1.add_container(lbl)

btn = tk.Button(p1.frame, text="Label Images", command=partial(switch_pages, p1, p2))
p1.add_container(btn)
btn = tk.Button(p1.frame, text="Process Data", command=partial(switch_pages, p1, "Process Data"))
p1.add_container(btn)



#Label Images Inputs Page construction 
lbl = tk.Label(p2.frame, text="Select the folder where your images are located.")
p2.add_container(lbl)
btn = tk.Button(p2.frame, text="Browse Folders", command = select_input_folder)
p2.add_container(btn)
lbl = tk.Label(p2.frame, textvariable=image_folder)
args = {"pady":(0, 20)}
p2.add_container(lbl, args=args)

lbl = tk.Label(p2.frame, text="Select the filetpye of your images.")
p2.add_container(lbl)
image_types = {"JPG", "PNG", "JPEG"}
pop_down_menu = tk.OptionMenu(p2.frame, image_type, *image_types)
args = {"pady":(0, 20)}
p2.add_container(pop_down_menu, args=args)

lbl = tk.Label(p2.frame, text="Select the folder where you want your results saved.")
p2.add_container(lbl)
btn = tk.Button(p2.frame, text="Browse Folders", command = select_output_folder)
p2.add_container(btn)
lbl = tk.Label(p2.frame, textvariable=output_folder)
args = {"pady":(0, 20)}
p2.add_container(lbl, args=args)

btn = tk.Button(p2.frame, text="Next", command=partial(switch_pages, p2, p3))
p2.add_container(btn)
btn = tk.Button(p2.frame, text="Back", command=partial(switch_pages, p2, p1))
p2.add_container(btn)



#Label Images Labelling Page construction 


btn = tk.Button(p3.frame, text="Next Image", command="")
p3.add_container(btn)
btn = tk.Button(p3.frame, text="Back", command=partial(switch_pages, p3, p2))
p3.add_container(btn)



#Linking Pages 
p1.add_child(p2)
p2.add_child(p3)

p1.turn_on()
window.mainloop()