import arcpy
import os


class ContainedNearestCentroidTool(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""

        self.label = "Contained Nearest centroid"
        self.description = "Finds the point contained within a polygon that is nearest to the polygon's centroid"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Polygon Features",
            name="in_polygons",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param0.filter.list = ["Polygon"]

        param1 = arcpy.Parameter(
            displayName="Point Features",
            name="in_points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param1.filter.list = ["Point"]

        param2 = arcpy.Parameter(
            displayName="Output Workspace",
            name="in_outws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param2.defaultEnvironmentName = "workspace"

        return [param0, param1, param2]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""

        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        polygons = parameters[0].valueAsText
        points = parameters[1].valueAsText
        out_ws = parameters[2].valueAsText

        polygon_id_field = get_well_known_id_field(polygons)
        point_id_field = get_well_known_id_field(points)

        tmp_poly_lyr = "tmp_poly_lyr"

        poly_search_cursor = arcpy.da.UpdateCursor(polygons, ['SHAPE@XY', 'OID@'])
        results = {}

        for poly_row in poly_search_cursor:

            poly_centroid = poly_row[0]
            polygon_id = poly_row[1]

            if arcpy.Exists(tmp_poly_lyr):
                arcpy.Delete_management(tmp_poly_lyr)

            where = '"{}" = {}'.format(polygon_id_field, polygon_id)
            try:
                arcpy.MakeFeatureLayer_management(polygons, tmp_poly_lyr, where)
                messages.AddMessage("Temp layer for feature ID = {} created".format(polygon_id))
            except:
                messages.AddWarning("Could not created temp layer for feature ID = {}".format(polygon_id))
                continue

            arcpy.SelectLayerByLocation_management(points, "WITHIN", tmp_poly_lyr)

            count = int(arcpy.GetCount_management(points).getOutput(0))
            messages.AddMessage("{} points within polygon".format(count))
            if count == 0:
                continue

            point_search_cursor = arcpy.da.SearchCursor(points, ['SHAPE@', 'OID@'])

            poly_centroid_pt = arcpy.Point()
            poly_centroid_pt.X, poly_centroid_pt.Y = poly_centroid

            dists = [(row[1], row[0].distanceTo(poly_centroid_pt)) for row in point_search_cursor]
            messages.AddMessage("distances are {}".format(dists))

            min_dist = min([dist for oid, dist in dists])
            minimums = [(oid, dist) for oid, dist in dists if dist == min_dist]
            messages.AddMessage("minimum is {}".format(minimums))

            if len(minimums) > 1:
                messages.AddMessage("multiple minimum distances, taking first found as result".format(minimums))

            minimums = minimums[0]
            messages.AddMessage("Result is PointID = {} Distance = {}".format(*minimums))

            results[minimums[0]] = minimums[1]

        if results:

            result_ds_name = arcpy.ValidateTableName("nearest_to_centroid_in_containing_polygon", out_ws)
            result_ds_name = os.path.join(out_ws, result_ds_name)
            where = '"{}" IN {}'.format(point_id_field, tuple(results.keys()))

            try:

                arcpy.SelectLayerByAttribute_management(points, "NEW_SELECTION", where)
                if arcpy.Exists(result_ds_name):
                    arcpy.Delete_management(result_ds_name)
                arcpy.CopyFeatures_management(points, result_ds_name)

            except Exception as e:
                messages.AddError("Error creating result dataset '{}' : {}".format(result_ds_name, e))

            messages.AddMessage("Result dataset '{}' created".format(result_ds_name))

        return


def get_well_known_id_field(dataset):

    fields = [f.name for f in arcpy.ListFields(dataset)]

    x_fields = tuple(
        set(fields).intersection(["OBJECTID", "OID", "FID"]))

    if not x_fields:
        raise ValueError("Could not find a well-known ID field in dataset")

    id_field = tuple(x_fields)[0]

    return id_field