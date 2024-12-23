Hey Elizabeth,

This is my final project for NR426.

In this folder you will find several items:

DEM folder - This contains the DEM that I acquired from the USGS earth explorer online tool.
Shapes folder - This contains two folders with .shp - both of these were acquired from the city of Fort Collins GIS page.
	- Hydrology folder
	- Trails folder 

NR_426_FINAL_CAM.py - This is my finished script

NR426_FINAL_WALKTHROUGH_CAM - This is a powerpoint detailing what my pseducode specifically says and pictures/descriptions that prove or validate that my desired process was completed and how it was completed, step by step.


***
As a side note i decided to add an extra smaller layer of complexity and place my most desired features for analysis into a new folder called "Finished Layers"
You will not have this layer unless you create it. Its arbitrary and not needed for the script to run. You can see in the script comments where these OPTIONAL steps occur. The script runs with and without this with just some small adjustments. 

Originally I had planned on using the DEM layer to clip raster with my trails to get elevations. I tried different things for a few hours including buffering the trails by 2 feet to make a polygon which is needed to clip raster but I couldnt get that to work, I tried some 3D analysis tools and elevation profile but after a lot of googling and trying i decided it was above the class level and above my knowledge level as well. I decided to take the DEM and reformat and reproject is as this is a semi complicated multi step process that would be nessecery in many real world scenarios.

Cam Caron