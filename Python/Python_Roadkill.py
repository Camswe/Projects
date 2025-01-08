"""LAB4B by Cam Caron 2-18-24
The purpose of this lab is to analyze roadkill data within a specified
geodatabase. It counts the number of points collected solely by the observer EAH
and in total, including with partners. The script then identifies roadkill
sightings within Ulster County and outputs a feature class for these points.
Additionally, it calculates the number of points not within 200 feet of a road
and buffers the locations of Striped Skunk sightings in Ulster County by 0.25
miles. The script emphasizes error handling and informative comments to ensure
robustness and clarity."""




print("*** SCRIPT STARTING ***")
import arcpy

try:
    # Set the workspace to your geodatabase
    arcpy.env.workspace = r"C:\Users\Allards Rigs #36\Documents\Lesson4LabData\RoadkillData.gdb"

    # Define feature class names
    roadkill_fc = "RoadkillSightings"
    roads_fc = "HRVRoads"
    counties_fc = "HRVCounties"

    # Check if the feature classes exist before proceeding
    if not arcpy.Exists(roadkill_fc) or not arcpy.Exists(roads_fc) or not arcpy.Exists(counties_fc):
        raise Exception("One or more of the specified feature classes do not exist in the geodatabase.")

    # 1. Count points collected solely by EAH
    query_eah_solo = "OBSERVER = 'EAH'"
    if arcpy.Exists("eah_solo_view"):
        arcpy.Delete_management("eah_solo_view")
    eah_solo_count = arcpy.management.GetCount \
        (arcpy.management.MakeTableView(roadkill_fc, "eah_solo_view", query_eah_solo)).getOutput(0)

    # 2. Count total points EAH collected, including those with partners
    query_eah_total = "OBSERVER LIKE '%EAH%'"
    if arcpy.Exists("eah_total_view"):
        arcpy.Delete_management("eah_total_view")
    eah_total_count = arcpy.management.GetCount \
        (arcpy.management.MakeTableView(roadkill_fc, "eah_total_view", query_eah_total)).getOutput(0)

    # The SQL query uses a LIKE operator to find all occurrences where 'EAH' appears in the OBSERVER field.
    # This includes entries where EAH collected points alone ('EAH') or with partners (e.g., 'EAH/JLB').
    #query_eah_total = "OBSERVER LIKE '%EAH%'"
    #if arcpy.Exists("eah_total_view"):
        #arcpy.Delete_management("eah_total_view")
    #eah_total_count = arcpy.management.GetCount(
        #arcpy.management.MakeTableView(roadkill_fc, "eah_total_view", query_eah_total)).getOutput(0)


    # 3. Create an output feature class of points within Ulster County
    query_ulster = "COUNTY = 'Ulster'"
    ulster_county_layer = arcpy.management.MakeFeatureLayer(counties_fc, "ulster_layer", query_ulster)
    selected_roadkills_in_ulster = arcpy.management.SelectLayerByLocation(roadkill_fc, "WITHIN", ulster_county_layer)
    output_fc_name = "Roadkill_In_Ulster"
    arcpy.management.CopyFeatures(selected_roadkills_in_ulster, output_fc_name)

    # 4. Count points not within 200 feet of a road
    not_near_road_layer = arcpy.management.SelectLayerByLocation(roadkill_fc, "WITHIN_A_DISTANCE_GEODESIC", roads_fc, "200 Feet", "NEW_SELECTION", "INVERT")
    not_near_road_count = arcpy.management.GetCount(not_near_road_layer).getOutput(0)

    # 5. Buffer Striped Skunk points in Ulster County by 0.25 miles
    query_skunk = "OBSERVER LIKE '%EAH%' AND Species = 'Striped Skunk'"
    skunk_in_ulster = arcpy.management.SelectLayerByAttribute(selected_roadkills_in_ulster, "NEW_SELECTION", query_skunk)
    output_buffer_name = "StripedSkunk_Ulster_Buffer"
    arcpy.analysis.Buffer(skunk_in_ulster, output_buffer_name, "0.25 Miles")

    # Inform the user about the results with reduced print calls
    print(f"EAH collected {eah_solo_count} points alone.")
    print(f"EAH collected a total of {eah_total_count} points (including with partners).\n")
    print(f"Output feature class of points within Ulster County created at: {arcpy.env.workspace}\\{output_fc_name}\n")
    print(f"{not_near_road_count} points are NOT within 200 feet of a road.\n")
    print(f"Buffered Striped Skunk points created at: {arcpy.env.workspace}\\{output_buffer_name}")


except arcpy.ExecuteError:
    # Catch any geoprocessing errors
    print(arcpy.GetMessages(2))
except Exception as e:
    # Catch any other errors
    print(e)

print("*** SCRIPT ENDED ***")
