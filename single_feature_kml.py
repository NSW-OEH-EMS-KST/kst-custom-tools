import arcpy
import os


class SingleFeatureKmlTool(object):

    def __init__(self):

        self.label = "Single feature KML"
        self.description = "Exports features into individual KML files"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="Features to Export",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Features ID Field",
            name="in_features_id",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        param1.parameterDependencies = ["in_features"]  # should be constant

        param2 = arcpy.Parameter(
            displayName="Output Workspace",
            name="in_outws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param2.defaultEnvironmentName = "workspace"

        return [param0, param1, param2]

    def isLicensed(self):

        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):

        features = parameters[0].valueAsText
        feature_id_field = parameters[1].valueAsText
        out_ws = parameters[2].valueAsText

        feat_search_cursor = arcpy.da.SearchCursor(features, [feature_id_field])

        for feat_row in feat_search_cursor:

            feat_id = feat_row[0].strip().replace(" ", "-")

            tmp_lyr = feat_id

            if arcpy.Exists(tmp_lyr):
                arcpy.Delete_management(tmp_lyr)

            where = "{} = '{}'".format(arcpy.AddFieldDelimiters(features, feature_id_field), feat_id)

            try:
                arcpy.MakeFeatureLayer_management(features, tmp_lyr, where)
                messages.addMessage("Temp layer for feature ID = {} created".format(feat_id))
            except Exception as e:
                messages.addWarningMessage("Could not create temp layer for feature ID = {}: {}".format(feat_id, e))
                continue

# LayerToKML_conversion(layer, out_kmz_file, {layer_output_scale}, {is_composite}, {boundary_box_extent}, {image_size}, {dpi_of_client}, {ignore_zvalue})
            out_kmz = os.path.join(out_ws, "{}_{}_{}.kmz".format(features, feature_id_field, feat_id))
            arcpy.LayerToKML_conversion(tmp_lyr, out_kmz)
            arcpy.Delete_management(tmp_lyr)

            messages.addMessage("KML '{}' created".format(out_kmz))

        return
