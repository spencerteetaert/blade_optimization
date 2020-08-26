import tkinter as tk

#Styles 
H1 = {"font":("Arial", 12, "bold"), "padx":20, "pady":10}
H2 = {"font":("Arial", 10, "bold"), "padx":15, "pady":7}
H3 = {"font":("Arial", 8, "bold"), "padx":10, "pady":5}
P1 = {"font":("Arial", 8), "padx":5, "pady":5}
P2 = {"font":("Arial", 8, "italic"), "padx":5, "pady":5}

def BTNF_BACK():
    pass

def BTNF_LABEL_IMAGES():
    print("Opening labelling images...")

    # Hides previous window 
    btn_process_images.pack_forget()
    btn_label_images.pack_forget()
    lbl_main_desc.pack_forget()

def BTNF_PROCESS_IMAGES():
    print("Opening processing images...")
    pass

#Main window construction 
window = tk.Tk()
window.geometry('500x500')
window.resizable(width=False, height=False)
window.title("Blade Optimization for Dummies")

#Frame constructions 
F1 = tk.Frame(window) # Landing page

F2 = tk.Frame(window) # Label images page
# F2_display = tk.Frame(F2)
F2_controls = tk.Frame(F2)

F3 = tk.Frame(window) # Process images frame
F3_controls = tk.Frame(F3)
F3_display = tk.Frame(F3)

lbl_main_desc = tk.Label(window, text="What would you like to do today?", **H3)
lbl_main_desc.pack()

#Buttons 
btn_label_images = tk.Button(window, text="Label Images", command=BTNF_LABEL_IMAGES, **H2)
btn_process_images = tk.Button(window, text="Process Images", command=BTNF_PROCESS_IMAGES, **H2)
btn_back = tk.Button(window, text="Back", command=BTNF_BACK, state="disabled", **H2)

btn_label_images.pack(padx=30, pady=10)
btn_process_images.pack(padx=30, pady=10)
btn_back.pack()

window.mainloop()