# blade_optimization
This project aims at generating the optimal shape for a cutting blade used for an industrial loin puller application. The new design should reduce the amount of exposed lean to enhance product quality. The source library contains tools for labelling, adjusting, and generating an optimal shape based off the specific data types available to me. The software was not developed with generality in mind, rather it was design for a specific application using specific data types. 

## What's inside?

### label_images.py 
This file contains a script that given an input folder location, allows me to label the data I have appropriately. It allows me to properly scale the image, adjust for rotation of the loin, and mark out where an optimum cut should be. It does this by taking the points I input and adding a variable fat thickness in a direction perpendicular to the lean line. The interface allows me to set and delete points, adjust the fat thickness between points, and save the data labelled into a usable form for analysis later. 

<p align="center">
  <img src="/resources/images/image_labelling.PNG" height="500">
</p>

### alignment.py
Due to large variable in the location of the meat in the input data set, a way to adjust their positioning needed to be determined for determination of an optimum shape later. This is only the case because the machine can move the blade, and so, we only care about the general shape generated. This file allows a user to manually adjust the position of a loaded data set so that the shapes of each loin are aligned. This method was chosen as it was faster than an algorithmic approach to implement on the relatively small data set available. 

<p align="center">
  <img src="/resources/images/alignment_tool_results.PNG">
</p>

### contours.py
A library containing functions to adjust contours as required by the application. 

### curves.py 
A library containing functions for curve fitting and displaying results. 

### geometry.py 
A library with various geometric functions for finding different variables. 

### process_data.py 
This file is what takes the labelled data and generates a shape. It does this through a series of steps:
* Load in the labelled data and smooth it. This accounts for random variation in the biology of plants and aids in creating a design that is manufacturable. 
* Remove any points that are irrelevant to ana actual cut. These are any points that the blade will not be able to cut, such as above the piece of meat. 
* Combine and align the resultant set of points on a polar axis 
* "Deviate" the points. This step takes each point and extends its radius to the 90th percentile of the surrounding points. This accounts for variation in loin shape and sizes.
* Fit a curve to the data with the following physical constraints to fulfill blade mounting requirements:
  * The slope of r must be 0 at the endpoints (8 inches apart).
  * The blade must end on the endpoints (8 inches apart). 
* Return the parameters of the curve for use in 3D CAD software where the shape will be joined with the existing mounting model. 

<p align="center">
  <img src="/resources/images/final_plot.png">
</p>

The fit determined here evaluated between -140° and -40° (the range in which data is available) is then used in a 3D CAD modelling software to create a model of the final blade shown below. 

<p align="center">
  <img src="/resources/images/final_blade.PNG" height="500">
</p>
