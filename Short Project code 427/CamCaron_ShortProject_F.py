'''Short Project - Cam Caron - 4-18-2024
This script is designed to process geospatial data to understand the distribution of snow monitoring stations across
various cities. It performs several key functions:
- Data Loading and Cleaning: It loads snow depth data from a CSV file, performs necessary data cleaning and then
saves the cleaned data to a new CSV file.
- Geospatial Layer Creation: Utilizing ArcPy, a Python library for ArcGIS, the script converts cleaned CSV data into a
spatially enabled point layer representing snow depth monitoring stations. It also loads a municipal boundary layer
from an online feature service.
- Spatial Analysis: The script conducts a spatial join between the snow depth monitoring stations and the municipal
boundaries. This operation identifies which monitoring stations fall within each municipal area.
- Data Aggregation and Reporting: After performing the spatial join, the script aggregates the data to calculate the
number of monitoring stations within each city. It then prints a consolidated report, listing each city with the
count of monitoring stations it contains.
- Error Handling: Throughout the process, the script includes error handling to manage potential issues such as
missing files, data parsing errors, and ArcGIS-specific errors, ensuring smooth and clear error reporting.'''

import pandas as pd
import arcpy
from arcpy import env
import os

# Define paths - CHANGE AS NEEDED
workspace_dir = "C:/Users/Allards Rigs #36/Documents/ArcGIS/Projects/short"
data_dir = "C:/Users/Allards Rigs #36/Downloads/Lesson 1 Data"
original_csv_name = "CO-snow-depth-202102.csv"
new_csv_name = "COsnow2021.csv"
feature_se_url = "https://services3.arcgis.com/DgjqnJA1rgO92Soi/arcgis/rest/services/Municipal_Boundary/FeatureServer/0"

print("*** Script Starting ***")

# Environment setup
env.workspace = workspace_dir
env.overwriteOutput = True

try:
    # Load and clean data from CSV
    original_csv_path = os.path.join(data_dir, original_csv_name)
    new_csv_path = os.path.join(data_dir, new_csv_name)

    if not os.path.exists(original_csv_path):
        raise FileNotFoundError(f"CSV file not found at {original_csv_path}")

    data = pd.read_csv(original_csv_path, header=1)
    print("Column Names in CSV:", data.columns.tolist())
    print("")

    if 'Elevation' not in data.columns or 'Latitude' not in data.columns:
        raise ValueError("Required columns are missing in the CSV file.")

    data['Elevation'] = pd.to_numeric(data['Elevation'], errors='coerce')
    data.dropna(subset=['Latitude', 'Elevation'], inplace=True)

    # Save the cleaned data to the new CSV
    data.to_csv(new_csv_path, index=False)
    print(f"Processed data saved to '{new_csv_path}'.")
    print("")

    # Create and save layers
    snow_depth_layer = arcpy.management.XYTableToPoint(new_csv_path, "SnowDepthLayer", "Longitude", "Latitude",
                                                       coordinate_system=arcpy.SpatialReference(4326))
    snow_depth_layer_file = arcpy.management.MakeFeatureLayer(snow_depth_layer, "SnowDepthLayerStyled")
    arcpy.management.SaveToLayerFile(snow_depth_layer_file,
                                     os.path.join(workspace_dir, "SnowDepthLayer.lyrx"))

    municipal_boundary_layer = arcpy.MakeFeatureLayer_management(feature_se_url, "MunicipalBoundary")
    arcpy.management.SaveToLayerFile(municipal_boundary_layer,
                                     os.path.join(workspace_dir, "MunicipalBoundaryLayer.lyrx"))

    print("Feature Service Layer Created: MunicipalBoundaryLayer.lyrx")
    print("")

    # Print feature types and counts
    snow_depth_desc = arcpy.Describe(snow_depth_layer_file)
    municipal_desc = arcpy.Describe(municipal_boundary_layer)
    snow_depth_count = arcpy.GetCount_management(snow_depth_layer_file)
    municipal_boundary_count = arcpy.GetCount_management(municipal_boundary_layer)

    print(f"Snow Depth Layer Type: {snow_depth_desc.shapeType}, Count: {snow_depth_count}")
    print(f"Municipal Boundary Layer Type: {municipal_desc.shapeType}, Count: {municipal_boundary_count}")
    print("")

    # Perform the spatial join
    join_output = os.path.join(workspace_dir, "SpatialJoinResult.shp")
    arcpy.analysis.SpatialJoin(target_features=municipal_boundary_layer, join_features=snow_depth_layer_file,
                               out_feature_class=join_output, join_type="KEEP_COMMON", match_option="INTERSECTS")

    print("Spatial join completed. Check the 'SpatialJoinResult.shp' for details.")
    print("")

    # Dictionary to hold the number of stations per city count
    stations_per_city_count = {}

    # Use a search cursor to go through the spatial join results
    with arcpy.da.SearchCursor(join_output, ["cityname", "Join_Count"]) as cursor:
        for row in cursor:
            count = row[1]
            city = row[0]
            if count in stations_per_city_count:
                stations_per_city_count[count].append(city)
            else:
                stations_per_city_count[count] = [city]

    # Print out consolidated city counts
    for count, cities in sorted(stations_per_city_count.items()):
        station_word = "station" if count == 1 else "stations"
        city_list = ", ".join(sorted(cities))
        print(f"There are {count} {station_word} in {city_list}")

# Error handling and final print
except FileNotFoundError as e:
    print(f"Error: {e}")
except pd.errors.EmptyDataError:
    print("Error: The CSV file is empty or corrupted.")
except pd.errors.ParserError:
    print("Error: There was a problem parsing the CSV file.")
except arcpy.ExecuteError as e:
    print(f"Error: ArcPy related error - {arcpy.GetMessages(2)}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("")
print("*** Script Completed Successfully ***")
