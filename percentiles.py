import arcpy
import arcpy.mapping
import os
import numpy
from collections import OrderedDict


class PercentilesTool(object):

    def __init__(self):

        self.label = "Calculate Field Value Percentiles"
        self.description = "Calculates numeric field value percentiles"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="Input Layer",
            name="in_features",
            datatype=["GPFeatureLayer", "GPRasterLayer"],
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Field of Interest (Numeric)",
            name="in_features_field",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        param1.parameterDependencies = [param0.name]
        param1.filter.list = ["Short", "Long", "Single", "Double"]

        # param2 = arcpy.Parameter(
        #     displayName="Number of intervals",
        #     name="num_intervals",
        #     datatype="GPLong",
        #     parameterType="Required",
        #     direction="Input")
        #
        # param2.value = 10

        param3 = arcpy.Parameter(
            displayName="Output Workspace",
            name="in_outws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param3.defaultEnvironmentName = "workspace"

        return [param0, param1, param3]  #, param2]  #, param4, param5, param6]

    # def isLicensed(self):
    #
    #     return True
    #
    # def updateParameters(self, parameters):
    #
    #     return
    #
    # def updateMessages(self, parameters):
    #
    #     return

    def execute(self, parameters, messages):

        parameter_dictionary = OrderedDict([(p.DisplayName, p.valueAsText) for p in parameters])
        parameter_summary = ", ".join(["{}: {}".format(k, v) for k, v in parameter_dictionary.iteritems()])
        messages.addMessage("Parameter summary: {}".format(parameter_summary))

        in_layer, in_fieldname, out_ws = parameter_dictionary.values()

        in_fields = [f.name for f in arcpy.ListFields(in_layer)]
        messages.addMessage("Fields in dataset '{}' are '{}'".format(in_layer, in_fields))

        in_layer = arcpy.mapping.Layer(in_layer)
        in_layer_desc = arcpy.Describe(in_layer)
        in_layer_path = in_layer_desc.catalogPath
        in_layer_dtype = in_layer_desc.dataType

        messages.addMessage("Input layer path, type = '{}', '{}".format(in_layer_path, in_layer_dtype))

        # num_quantiles = num_intervals - 1
        # messages.addMessage("Intervals = '{}' -->> quantiles =  '{}".format(num_intervals, num_quantiles))

        arr = arcpy.da.FeatureClassToNumPyArray(in_layer, in_fieldname)
        arr = arr.astype(numpy.float32)
        messages.addMessage(arr)

        v = []
        for i in range(1, 99):
            p = numpy.percentile(arr, i)
            v.append(p)  # rank = 0
            messages.addMessage("{}-percentile = {}".format(i, v))


        # p2 = np.percentile(arr, 67)  # rank = 1
        # p3 = np.percentile(arr, 100)  # rank = 2
        #
        # #use cursor to update the new rank field
        # with arcpy.da.UpdateCursor(input , ['population_density','PerRank']) as cursor:
        #     for row in cursor:
        #         if row[0] < p1:
        #             row[1] = 0  #rank 0
        #         elif p1 <= row[0] and row[0] < p2:
        #              row[1] = 1
        #         else:
        #              row[1] = 2
        #
        #         cursor.updateRow(row)
        # try:
        #     arcpy.SelectLayerByAttribute_management(in_layer, "CLEAR_SELECTION")
        #     messages.addMessage("Selection in layer '{}' cleared".format(in_layer))
        # except:
        #     pass
        #
        # try:
        #     arcpy.BuildRasterAttributeTable_management(in_layer)
        #     messages.addMessage("Fresh attribute table built")
        # except:
        #     pass
        #
        # try:
        #     data = arcpy.da.TableToNumPyArray(in_layer_path, in_fieldname)
        # except:
        #     try:
        #         data = arcpy.da.FeatureClassToNumPyArray(in_layer_path, in_fieldname)
        #     except:
        #         raise ValueError("Could not pull in Numpy array")
        #
        # unique_values = numpy.unique(data[in_fieldname])
        #
        # # unique_values = sorted({row[0] for row in arcpy.da.SearchCursor(in_layer, in_fieldname)})  # if row[0]})
        # unique_values_count = len(unique_values)
        # messages.addMessage("The input dataset field '{}' has {} unique values: {}".format(in_fieldname, unique_values_count, unique_values))
        #
        # cost_raster_names = OrderedDict([(value, make_output_name("cost_{}".format(value), out_ws)) for value in unique_values])
        #
        # messages.addMessage("Cost rasters to be generated: {}".format(cost_raster_names.values()))
        #
        # temp_layer = "temp_layer"
        #
        # for value in unique_values:
        #     messages.addMessage("Processing field value = {}".format(value))
        #
        #     if arcpy.Exists(temp_layer):
        #         arcpy.Delete_management(temp_layer)
        #
        #     where = '"{}" = {}'.format(in_fieldname, value)
        #     try:
        #         arcpy.SelectLayerByAttribute_management(in_layer, "NEW_SELECTION", where)
        #         cost = arcpy.sa.CostDistance(in_layer, cost_raster, max_cost_distance)
        #         messages.addMessage("\tCreated cost raster")
        #     except:
        #         messages.addWarningMessage("\tCould not create cost raster")
        #         cost_raster_names.pop(value)
        #         continue
        #     try:
        #         out_name = cost_raster_names[value]
        #         cost.save(out_name)
        #         messages.addMessage("\tSaved cost raster '{}'".format(out_name))
        #     except:
        #         messages.addWarningMessage("\tCould not create cost raster for field value = {}".format(value))
        #         cost_raster_names.pop(value)
        #         continue
        #
        # if not len(cost_raster_names):
        #
        #     raise ValueError("No cost rasters to sum")
        #
        # cost_rasters = cost_raster_names.values()
        #
        # sum_raster = nulls_to_zero(cost_rasters[0])
        # for cost_raster in cost_rasters[1:]:
        #     sum_raster += nulls_to_zero(cost_raster)
        #
        # out_name = make_output_name("cost_sum", out_ws)
        # sum_raster.save(out_name)
        # messages.addMessage("\tSaved summed cost raster to '{}'".format(out_name))
        #
        # try:
        #     arcpy.mapping.AddLayer(arcpy.mapping.ListDataFrames(arcpy.mapping.MapDocument("CURRENT"))[0], arcpy.Layer(out_name))
        #     messages.addMessage("'{}' added to map".format(out_name))
        # except:
        #     messages.addMessage("Could not add '{}' to map".format(out_name))
        #
        # if delete_costs == "true":
        #     messages.addMessage("Deleting individual cost rasters...")
        #     for r in cost_raster_names.values():
        #         arcpy.Delete_management(r)
        #         messages.addMessage("\tDeleted cost raster '{}'".format(r))
        #
        # try:
        #     arcpy.Compact_management(out_ws)
        #     messages.addMessage("Output workspace '{}' compacted".format(out_ws))
        # except:
        #     pass
        #
        # try:
        #     arcpy.SelectLayerByAttribute_management(in_layer, "CLEAR_SELECTION")
        # except:
        #     pass

        return

# def make_output_name(like_name, out_ws):
#
#     like_name = arcpy.ValidateTableName(like_name, out_ws)
#     like_name = arcpy.CreateUniqueName(like_name, out_ws)
#
#     return os.path.join(out_ws, like_name)
#
#
# def nulls_to_zero(in_raster):
#
#     return arcpy.sa.Con(arcpy.sa.IsNull(in_raster), 0, in_raster)
