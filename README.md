# blade_optimization

The blade optimization project is aimed at creating a method for which loin cutting blades can be rapidly designed using any desired cutting spec. It opens the doors to companies internally designing new blades when their cutting specs change, without the need for a third-party designer. A simple GUI was designed to allow non-programmer staff to contribute to the design process by specifying the cuts desired. 

The program works in three phases. The first is for employees to label cross sectional pieces of the cutting meat to specify what the ideal cut for that specific piece is. This process is repeated as many times as is feasible to collect lots of data. In the second phase, employees will align the data collected from phase one. This step is necessary and is meant to mimic the equipment's ability to adjust its height based on the product coming through. In lieu of not having access to said software, this alignment phase is a workaround. In the third phase the users will fit a curve to the data that has been collected and aligned. The curve has options to be expanded to consider a certain percentile, and various other fit parameters. The curve generated can then be used in each CAD modelling software to create a physical blade design. 

This software shortens the design process from up to months working with a third-party designer to less than a day. The designs are based on data that the designing plant is producing and not what the third-party had access to. On top of this, the designs are highly customizable to any cutting spec that a company desire. Need more cut from the belly side? Less? Want higher fat coverage? This software can create the design quickly and easily. 

## What's inside?
### alignment.py
Contains code that allows users to align their data to mimic the controls of existing equipment. 

![Alignment](/resources/images/Alignment.PNG)

### contours.py
Contains functions relating to the cv2 class contours 

### curves.py
Contains functions required for fitting curves. 

### data_io.py
Contains the read/write functions for intermediate data. 

### geometry.py (not in use) 
Contains geometric functions for different ways of selecting points. 

### label_images.py
Contains code that allows users to label images including specifying image scale, reference points, and ideal cut lines.

![Image Labelling](/resources/images/label_images.PNG)

### page.py
Contains a page class for GUI control. 

### process_data.py
Contains code that processes labelled data. Allows users to fit curves based on the aligned data. 

![Blade Fit](/resources/images/blade_fit.PNG)

### window.py 
Construction for GUI

### main.py 
Runs the program. 

![Home Page](/resources/images/home_page.PNG) ![Info Page](/resources/images/info_page.PNG)
