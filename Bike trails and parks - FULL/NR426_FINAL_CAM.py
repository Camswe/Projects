'''NR426 Final Project - Cam Caron
The aim of this project is to analyze bike-friendly trails within a 1-mile buffer
of Horsetooth Reservoir. The script automates the GIS processing workflow to:

1. Define the base and output directories for storing GIS data and results.
2. Set up the ArcPy environment and eable output data overwriting.
3. Project Trails and Hydrology shapefiles to WGS 84 spatial reference.
4. Project a DEM file to a suitable projected coordinate system (Web Mercator),
   then reproject to WGS 84 for consistent spatial analysis.
5. Filter the Hydrology layer to include only "Horsetooth Reservoir" and
   create a buffer of 1 mile around it.
6. Clip the Trails layer by the Horsetooth Reservoir buffer to focus on relevant
   trails, then select only those trails marked as bike-friendly.
7. Calculate the distance of each bike-friendly trail from the Horsetooth Reservoir
   using the Near tool.
8. Sort bike-friendly trails by their proximity to Horsetooth Reservoir and
   output the sorted list to the "Finished Layers" directory.
9. Use arcpy.GetCount_management to count the total number of bike-friendly trails
   within the specified buffer zone.
10. Output processing completion and the total count of bike-friendly trails, ensuring
    all data is organized and accessible in the specified output directory.
    '''

import arcpy
import os

print("*** SCRIPT STARTING ***")

# User-configurable section
# ==========================
# Define the parent directory where your data is located
parent_dir = r"C:\Users\Allards Rigs #36\Documents\NR426"

# Relative directories for shapefiles and DEM relative to the parent directory
shapes_dir = os.path.join(parent_dir, "Shapes")  # Adjust if your shapefiles are in a different subdirectory
dem_dir = os.path.join(parent_dir, "DEM")  # Adjust if your DEM files are in a different subdirectory
# ==========================
# OPTIONAL - Output directory for processed files, relative to the parent directory
output_dir = os.path.join(parent_dir, "Finished Layers")

# OPTIONAL - Ensure the output directory exists, create if not
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Set the workspace environment and enable overwriting of data
arcpy.env.workspace = parent_dir
arcpy.env.overwriteOutput = True

try:
    # Define file paths
    print("Defining file paths...")
    trails_shp = os.path.join(parent_dir, "Shapes", "Trails", "Trails.shp")
    hydrology_shp = os.path.join(parent_dir, "Shapes", "Hydrology", "Hydrology.shp")
    dem_tif = os.path.join(parent_dir, "DEM", "FCDEM.tif")

    # Ensure all shapefiles and DEM are in WGS 84 projection
    wgs84 = arcpy.SpatialReference(4326)
    projected_coor_system = arcpy.SpatialReference(3857)  # Web Mercator

    print("")
    print("Projecting GIS layers...")
    # Project GIS layers
    trails_wgs84 = arcpy.management.Project(trails_shp, os.path.join(output_dir, "Trails_WGS84.shp"), wgs84)
    hydrology_wgs84 = arcpy.management.Project(hydrology_shp, os.path.join(output_dir, "Hydrology_WGS84.shp"), wgs84)

    print("")
    print("Processing DEM...")
    projected_dem = arcpy.management.ProjectRaster(dem_tif, os.path.join(output_dir, "Projected_DEM.tif"),
                                                   projected_coor_system)
    DEM_wgs84 = arcpy.management.ProjectRaster(projected_dem, os.path.join(output_dir, "FCDEM_WGS84.tif"), wgs84)
    arcpy.management.Delete(projected_dem)  # Clean up temporary raster

    print("")
    print("Filtering and buffering Hydrology...")
    # Filter and buffer Hydrology
    query = "\"NAME\" = 'Horsetooth Reservoir'"
    hydro_layer_path = os.path.join(output_dir, "Horsetooth.shp")
    hydro_layer = arcpy.analysis.Select(hydrology_wgs84, hydro_layer_path, query)
    horsetooth_buffer = arcpy.analysis.Buffer(hydro_layer, os.path.join(output_dir, "Horsetooth_Buffer.shp"), "1 Miles",
                                              dissolve_option="NONE")
    print("")
    print("Clipping trails and selecting by BIKEUSE...")
    # Clip Trails and select by BIKEUSE
    trails_clipped_path = os.path.join(output_dir, "Trails_Clip.shp")
    trails_clipped_layer = arcpy.analysis.Clip(trails_wgs84, horsetooth_buffer, trails_clipped_path)
    arcpy.management.MakeFeatureLayer(trails_clipped_layer, "Trails_Clip_Layer")
    arcpy.management.SelectLayerByAttribute("Trails_Clip_Layer", "NEW_SELECTION", "BIKEUSE = 'Yes'")
    trails_bikeuse_yes = arcpy.management.CopyFeatures("Trails_Clip_Layer",
                                                       os.path.join(output_dir, "Trails_BikeUse_Yes.shp"))
    print("")
    print("Calculating distances from Horsetooth Reservoir...")
    # Calculate Near distances
    arcpy.analysis.Near(trails_bikeuse_yes, hydro_layer_path)

    print("")
    print("Sorting trails by distance...")
    # Sorting trails by distance
    # OPTIONAL output directory
    trails_sorted_by_distance = arcpy.management.Sort(trails_bikeuse_yes,
                                                      os.path.join(output_dir, "Bike_Trails_Sorted_By_Distance.shp"),
                                                      [["NEAR_DIST", "ASCENDING"]])

    # Use arcpy.GetCount_management to get the total count of bike-friendly trails
    total_bike_trails_count = arcpy.GetCount_management(trails_sorted_by_distance)
    print(f"Total number of bike-friendly trails within the 1 mile Horsetooth buffer: {total_bike_trails_count[0]}")


except Exception as e:
    print(f"Error encountered: {e}")

print("")
print("*** SCRIPT COMPLETED SUCCESSFULLY ***")
print("")
print("All layers projected, buffered, clipped, and calculated. Final data is located in 'Finished Layers' folder")
