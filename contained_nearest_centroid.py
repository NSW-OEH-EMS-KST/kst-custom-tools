import arcpy
import os
from datetime import datetime


class ContainedNearestCentroidTool(object):

    def __init__(self):

        self.label = "Contained Nearest Centroid"
        self.description = "Finds the point contained within a polygon that is nearest to the polygon's centroid"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="Polygon Features",
            name="in_polygons",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param0.filter.list = ["Polygon"]

        param1 = arcpy.Parameter(
            displayName="Polygon Features ID Field",
            name="in_polygons_id",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        param1.parameterDependencies = ["in_polygons"]  # should be constant

        param2 = arcpy.Parameter(
            displayName="Point Features",
            name="in_points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param2.filter.list = ["Point"]

        param3 = arcpy.Parameter(
            displayName="Point Features ID Field",
            name="in_points_id",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        param3.parameterDependencies = ["in_points"]  # should be constant

        param4 = arcpy.Parameter(
            displayName="Output Workspace",
            name="in_outws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param4.defaultEnvironmentName = "workspace"

        return [param0, param1, param2, param3, param4]

    def isLicensed(self):

        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):

        polygons = parameters[0].valueAsText
        polygon_id_field = parameters[1].valueAsText
        points = parameters[2].valueAsText
        point_id_field = parameters[3].valueAsText
        out_ws = parameters[4].valueAsText

        tmp_poly_lyr = "tmp_poly_lyr"

        poly_rows = [row for row in arcpy.da.UpdateCursor(polygons, ['SHAPE@XY', 'OID@'])]
        # poly_rows = ]
        total_rows = len(poly_search_cursor)
        row_num = 0
        results = {}

        for poly_row in poly_rows:

            poly_centroid = poly_row[0]
            polygon_id = poly_row[1]

            row_num += 1
            messages.addMessage("{} > Processing feature {} of {} with {} = {}".format(datetime.now().strftime("%H:%M:%S%f")[:-3], row_num, total_rows, polygon_id_field, polygon_id))
            # messages.addMessage("Processing feature ID = {}".format(polygon_id))

            if arcpy.Exists(tmp_poly_lyr):
                arcpy.Delete_management(tmp_poly_lyr)

            where = '"{}" = {}'.format(polygon_id_field, polygon_id)
            try:
                arcpy.MakeFeatureLayer_management(polygons, tmp_poly_lyr, where)
                # messages.addMessage("Temp layer for feature ID = {} created".format(polygon_id))
            except:
                messages.AddWarning("Could not created temp layer for feature ID = {}".format(polygon_id))
                continue

            arcpy.SelectLayerByLocation_management(points, "WITHIN", tmp_poly_lyr)

            count = int(arcpy.GetCount_management(points).getOutput(0))
            # messages.addMessage("{} points within polygon".format(count))
            if count == 0:
                continue

            point_search_cursor = arcpy.da.SearchCursor(points, ['SHAPE@', 'OID@'])

            poly_centroid_pt = arcpy.Point()
            poly_centroid_pt.X, poly_centroid_pt.Y = poly_centroid

            dists = [(row[1], row[0].distanceTo(poly_centroid_pt)) for row in point_search_cursor]
            # messages.addMessage("distances are {}".format(dists))

            min_dist = min([dist for oid, dist in dists])
            minimums = [(oid, dist) for oid, dist in dists if dist == min_dist]
            # messages.addMessage("minimum is {}".format(minimums))

            # if len(minimums) > 1:
            #     messages.addMessage("multiple minimum distances, taking first found as result".format(minimums))

            minimums = minimums[0]
            # messages.addMessage("Result is PointID = {} Distance = {}".format(*minimums))

            results[minimums[0]] = minimums[1]

        if results:
            where = '"{}" IN {}'.format(point_id_field, tuple(results.keys()))

            arcpy.SelectLayerByAttribute_management(points, "NEW_SELECTION", where)

            result_ds_name = "nearest_to_centroid_in_containing_polygon"
            if arcpy.Describe(out_ws).workspaceType == "FileSystem":
                result_ds_name += ".shp"
            result_ds_name = arcpy.ValidateTableName(result_ds_name, out_ws)
            result_ds_name = arcpy.CreateUniqueName(result_ds_name, out_ws)
            result_ds_name = os.path.join(out_ws, result_ds_name)

            try:
                arcpy.CopyFeatures_management(points, result_ds_name)
                messages.addMessage("Result dataset '{}' created".format(result_ds_name))
            except Exception as e:
                messages.addErrorMessage("Error creating result dataset '{}' : {}".format(result_ds_name, e))
                messages.addMessage("*** Export the selection in layer '{}' to save the results".format(points))

        return

