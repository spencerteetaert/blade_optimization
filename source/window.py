import tkinter as tk
from tkinter import filedialog
import threading
import cv2

from .page import *
from . import label_images
from . import process_data

#Styles 
H1 = {"font":("Arial", 12, "bold"), "padx":20, "pady":10}
H2 = {"font":("Arial", 10, "bold"), "padx":15, "pady":7}
H3 = {"font":("Arial", 8, "bold"), "padx":10, "pady":5}
P1 = {"font":("Arial", 8), "padx":5, "pady":5}
P2 = {"font":("Arial", 8, "italic"), "padx":5, "pady":5}

#Main window construction 
window = tk.Tk()
window.geometry('350x450')
window.resizable(width=False, height=False)
window.title("Blade Designer")

photo = tk.PhotoImage(file = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\welcome-logo.png")
window.iconphoto(False, photo)

# Page Initialization 
p1 = Page("Blade Designer", window)
p2 = Page("Label Images", window, p1)
p3 = Page("Label Images", window, p2)
p4 = Page("Process Images", window, p1)
p5 = Page("Process Images", window, p4)
p6 = Page("Program Info", window, p1)


#Page Functions
image_folder = tk.StringVar(window)
output_folder = tk.StringVar(window)
image_type = tk.StringVar(window)
input_data = tk.StringVar(window)
fat_thickness = tk.DoubleVar(window, value=12)
degree = tk.IntVar(window, value=8)
percentile = tk.DoubleVar(window, value=95)
dtheta = tk.DoubleVar(window, value=3)

def select_input_folder():
    global image_folder
    temp = tk.filedialog.askdirectory()
    image_folder.set(temp)
def select_output_folder():
    global output_folder
    temp = tk.filedialog.askdirectory()
    output_folder.set(temp)
def select_input_file():
    global input_data
    temp = tk.filedialog.askopenfilename()
    input_data.set(temp)
def into_labelling(p1, p2):
    global image_types, image_folder, output_folder
    switch_pages(p1, p2)
    # Creates a new thread with target function 
    t = threading.Thread(target = label_images.main, args=[image_folder.get(), image_type.get(), output_folder.get()])
    t.daemon = True
    t.start()
def next_image():
    label_images.display_break_flag = True
def finish_labelling():
    label_images.display_break_flag = True
    label_images.break_flag = True
def reset_points():
    label_images.state = "Setting Length"
    label_images.scale_points = []
    label_images.chosen_points = []
    label_images.peak_point = [0, 0]
def into_processing(p1, p2):
    global input_data
    switch_pages(p1, p2)
    # Creates a new thread with target function 
    t = threading.Thread(target = process_data.main, args=[input_data.get()])
    t.daemon = True
    t.start()

# Landing page construction 
lbl = tk.Label(p1.frame, text="What would you like to do today?")
p1.add_container(lbl)

btn = tk.Button(p1.frame, text="Label Images", command=partial(switch_pages, p1, p2))
p1.add_container(btn)
btn = tk.Button(p1.frame, text="Process Data", command=partial(switch_pages, p1, p4))
p1.add_container(btn)
btn = tk.Button(p1.frame, text="Program Info", command=partial(switch_pages, p1, p6))
p1.add_container(btn)

#Label Images Inputs Page construction 
lbl = tk.Label(p2.frame, text="Select the folder where your images are located.")
p2.add_container(lbl)
btn = tk.Button(p2.frame, text="Browse Folders", command = select_input_folder)
p2.add_container(btn)
lbl = tk.Label(p2.frame, textvariable=image_folder, wraplength=300, justify="center")
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
lbl = tk.Label(p2.frame, textvariable=output_folder, wraplength=300, justify="center")
args = {"pady":(0, 20)}
p2.add_container(lbl, args=args)

btn = tk.Button(p2.frame, text="Start Labelling", command=partial(into_labelling, p2, p3))
p2.add_container(btn)
btn = tk.Button(p2.frame, text="Back", command=partial(switch_pages, p2, p1))
p2.add_container(btn)

#Label Images Labelling Page construction 
lbl = tk.Label(p3.frame, text="Fat thickness (mm)")
p3.add_container(lbl)
fat_thickness_selector = tk.Spinbox(p3.frame, textvariable=fat_thickness, from_=0, to=50)
p3.add_container(fat_thickness_selector)

btn = tk.Button(p3.frame, text="Reset all Points [R]", command=reset_points)
p3.add_container(btn)
btn = tk.Button(p3.frame, text="Next Image [SPACE]", command=next_image)
p3.add_container(btn)
btn = tk.Button(p3.frame, text="Finish (and Save) [Q]", command=finish_labelling)
p3.add_container(btn)
btn = tk.Button(p3.frame, text="Back", command=partial(switch_pages, p3, p2))
p3.add_container(btn)

#Process Images Inputs Page construction 
lbl = tk.Label(p4.frame, text="Select the file generated from labelling images.")
p4.add_container(lbl)
btn = tk.Button(p4.frame, text="Browse Files", command = select_input_file)
p4.add_container(btn)
lbl = tk.Label(p4.frame, textvariable=input_data, wraplength=300, justify="center")
args = {"pady":(0, 20)}
p4.add_container(lbl, args=args)

btn = tk.Button(p4.frame, text="Start Processing", command=partial(into_processing, p4, p5))
p4.add_container(btn)
btn = tk.Button(p4.frame, text="Back", command=partial(switch_pages, p4, p1))
p4.add_container(btn)

#Process Images Page construction 
lbl = tk.Label(p5.frame, text="Degree of polynomial to fit to data.")
p5.add_container(lbl)
degree_selector = tk.Spinbox(p5.frame, textvariable=degree, from_=0, to=12)
p5.add_container(degree_selector)
lbl = tk.Label(p5.frame, text="Percentile of loins to be accounted for.")
p5.add_container(lbl)
percentile_selector = tk.Spinbox(p5.frame, textvariable=percentile, from_=0, to=100, increment=0.1)
p5.add_container(percentile_selector)
lbl = tk.Label(p5.frame, text="dtheta.")
p5.add_container(lbl)
dtheta_selector = tk.Spinbox(p5.frame, textvariable=dtheta, from_=0, to=50, increment=0.1)
p5.add_container(dtheta_selector)

btn = tk.Button(p5.frame, text="Solve Fit", command=process_data.find_best_fit)
p5.add_container(btn)
btn = tk.Button(p5.frame, text="Back", command=partial(switch_pages, p5, p4))
p5.add_container(btn)

#Program info page construction 
info = tk.Text(p6.frame, wrap=tk.WORD, height=20)
info_str = "Blade Designer v1.0\nBy Spencer Teetaert (Continuous Improvement)\n\n\
    Last updated on August 28, 2020\n\nSource code available at: https://github.com/spencerteetaert/blade_optimization\n\n\
    No updates for this software are planned."
info.insert("end", info_str)
info['state'] = "disabled"
p6.add_container(info)

btn = tk.Button(p6.frame, text="Back", command=partial(switch_pages, p6, p1))
p6.add_container(btn)

#Linking Pages 
p1.add_child(p2)
p1.add_child(p4)
p1.add_child(p6)
p2.add_child(p3)
p4.add_child(p5)

p1.turn_on()

def run():
    window.mainloop()