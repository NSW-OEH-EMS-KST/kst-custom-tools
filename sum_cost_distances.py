import arcpy
import arcpy.mapping
from arcpy import env
import os
from collections import OrderedDict


class SumCostDistancesTool(object):

    def __init__(self):

        self.label = "Sum Cost Distances"
        self.description = "Sums cost distances calculated on unique input feature field values"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="Features",
            name="in_features",
            datatype=["GPFeatureLayer", "GPRasterLayer"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Field of Interest",
            name="in_features_field",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        param1.parameterDependencies = [param0.name]

        param2 = arcpy.Parameter(
            displayName="Cost Raster",
            name="in_cost_raster",
            datatype=["DERasterDataset", "GPRasterLayer"],
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Maximum Cost Distance",
            name="in_max_cost_distance",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Output Raster Cell Size",
            name="in_out_raster_cellsize",
            datatype="GPSACellSize",
            parameterType="Optional",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Output Workspace",
            name="in_outws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param5.defaultEnvironmentName = "workspace"

        param6 = arcpy.Parameter(
            displayName="Delete Individual Cost Rasters",
            name="delete_costs",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        param6.value = False

        return [param0, param1, param2, param3, param4, param5, param6]

    def isLicensed(self):

        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):

        parameter_dictionary = OrderedDict([(p.DisplayName, p.valueAsText) for p in parameters])
        parameter_summary = ", ".join(["{}: {}".format(k, v) for k, v in parameter_dictionary.iteritems()])
        messages.addMessage("Parameter summary: {}".format(parameter_summary))

        features, features_fieldname, cost_raster, max_cost_distance, out_raster_cellsize, out_ws, delete_costs = parameter_dictionary.values()

        fields = [f.name for f in arcpy.ListFields(features)]
        messages.addMessage("Fields available in dataset are {}".format(fields))

        features = arcpy.mapping.Layer(features)

        try:
            arcpy.SelectLayerByAttribute_management(features, "CLEAR_SELECTION")
            messages.addMessage("Selection in layer '{}' cleared".format(features))
        except:
            pass
#
        unique_values = sorted({row[0] for row in arcpy.da.SearchCursor(features, features_fieldname)})  # if row[0]})
        unique_values_count = len(unique_values)
        messages.addMessage("The feature dataset field '{}' has {} unique values: {}".format(features_fieldname, unique_values_count, unique_values))

        cost_raster_names = OrderedDict([(value, make_output_name("cost_{}".format(value), out_ws)) for value in unique_values])

        messages.addMessage("Cost rasters to be generated: {}".format(cost_raster_names.values()))

        temp_layer = "temp_layer"
        arcpy.env.workspace = "in_memory"

        for value in unique_values:
            messages.addMessage("Processing field value = {}".format(value))

            if arcpy.Exists(temp_layer):
                arcpy.Delete_management(temp_layer)

            where = '"{}" = {}'.format(features_fieldname, value)
            arcpy.SelectLayerByAttribute_management(features, "NEW_SELECTION", where)
            try:
                cost = arcpy.sa.CostDistance(features, cost_raster, max_cost_distance)
                arcpy .CalculateStatistics_management(cost)
                # normalise
                messages.addMessage("\tNormalising")
                cost = (cost - cost.minimum)/(cost.maximum - cost.minimum)
                # invert
                messages.addMessage("\tInverting")
                cost = arcpy.sa.Abs(cost - 1)
                # scaling
                messages.addMessage("\tScaling")
                cost = cost * value  # test this
                messages.addMessage("\tCreated cost raster")
            except Exception as e:
                messages.addWarningMessage("\tCould not create cost raster: {}".format(str(e)))
                cost_raster_names.pop(value)
                continue
            try:
                out_name = cost_raster_names[value]
                cost.save(out_name)
                messages.addMessage("\tSaved cost raster '{}'".format(out_name))
            except:
                messages.addWarningMessage("\tCould not create cost raster for field value = {}".format(value))
                cost_raster_names.pop(value)
                continue

        if not len(cost_raster_names):

            raise ValueError("No cost rasters to sum")

        cost_rasters = cost_raster_names.values()

        sum_raster = nulls_to_zero(cost_rasters[0])
        for cost_raster in cost_rasters[1:]:
            sum_raster += nulls_to_zero(cost_raster)

        sum_raster.save(make_output_name("cost_sum", out_ws))

        if delete_costs == "true":
            messages.addMessage("Deleting individual cost rasters...")
            for r in cost_raster_names.values():
                arcpy.Delete_management(r)
                messages.addMessage("\tDeleted cost raster '{}'".format(r))

        try:
            arcpy.Compact_management(out_ws)
            messages.addMessage("Output workspace '{}' compacted".format(out_ws))
        except:
            pass

        try:
            arcpy.SelectLayerByAttribute_management(features, "CLEAR_SELECTION")
        except:
            pass


def make_output_name(like_name, out_ws):

    like_name = arcpy.ValidateTableName(like_name, out_ws)
    like_name = arcpy.CreateUniqueName(like_name, out_ws)

    return os.path.join(out_ws, like_name)


def nulls_to_zero(in_raster):

    return arcpy.sa.Con(arcpy.sa.IsNull(in_raster), 0, in_raster)
