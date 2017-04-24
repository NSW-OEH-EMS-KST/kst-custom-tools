import arcpy
import os
from collections import OrderedDict


class SumCostDistancesTool(object):

    def __init__(self):

        self.label = "Sum of Cost Distances by Unique Field Values"
        self.description = "Sums cost distances calculated on unique input field values"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param0.filter.list = ["Polyline"]

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
            displayName="Save Individual Cost Rasters",
            name="save_costs",
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
        messages.AddMessage("Parameter summary: {}".format(parameter_summary))

        features, features_fieldname, cost_raster, max_cost_distance, out_raster_cellsize, out_ws, save_costs = parameter_dictionary.values()

        try:
            arcpy.SelectLayerByAttribute_management(features, "CLEAR_SELECTION")
            messages.AddMessage("Selection in layer {} cleared".format(features))
        except:
            pass

        unique_orders = sorted({row[0] for row in arcpy.da.SearchCursor(features, features_fieldname) if row[0]})
        unique_orders_count = len(unique_orders)
        messages.AddMessage("The feature dataset field {} has {} unique values: {}".format(features_fieldname, unique_orders_count, unique_orders))

        cost_raster_names = OrderedDict([(order, "cost_{}".format(order)) for order in unique_orders])
        cost_raster_names = {k: arcpy.ValidateTableName(v, out_ws) for k, v in cost_raster_names.iteritems()}
        cost_raster_names = {k: os.path.join(out_ws, v) for k, v in cost_raster_names.iteritems()}

        messages.AddMessage("cost rasters to be generated: {}".format(cost_raster_names.values()))

        temp_layer = "temp_layer"

        for order in unique_orders:
            messages.AddMessage("Processing field value = {}".format(order))

            if arcpy.Exists(temp_layer):
                arcpy.Delete_management(temp_layer)

            where = '"{}" = {}'.format(features_fieldname, order)
            arcpy.SelectLayerByAttribute_management(features, "NEW_SELECTION", where)
            try:
                cost = arcpy.sa.CostDistance(features, cost_raster, max_cost_distance)
                out_name = cost_raster_names[order]
                cost.save(out_name)
                messages.AddMessage("Created cost raster {}".format(out_name))
            except:
                messages.AddMessage("Could not create cost raster for field value = {}".format(order))
                cost_raster_names.pop(order)
                continue

        if not len(cost_raster_names):

            raise ValueError("No cost rasters to sum")

        rasters_to_sum = cost_raster_names.values()

        sum_raster = arcpy.Raster(rasters_to_sum[0])
        for raster in rasters_to_sum[1:]:
            sum_raster += raster

        sum_raster_name = "cost_sum"
        sum_raster_name = arcpy.ValidateTableName(sum_raster_name, out_ws)
        sum_raster_name = os.path.join(out_ws, sum_raster_name)

        sum_raster.save(sum_raster_name)

        if not save_costs == "false":
            for r in cost_raster_names.values():
                arcpy.Delete_management(r)

        try:
            arcpy.Compact_management(out_ws)
        except:
            pass
