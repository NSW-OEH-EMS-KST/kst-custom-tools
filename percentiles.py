import arcpy
import arcpy.mapping
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

        param3 = arcpy.Parameter(
            displayName="Output Workspace",
            name="in_outws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param3.defaultEnvironmentName = "workspace"

        return [param0, param1, param3]

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

        arr = arcpy.da.FeatureClassToNumPyArray(in_layer, in_fieldname).astype(numpy.float32)
        ndv = arcpy.Raster(in_layer).noDataValue

        messages.addMessage("Input layer path, type, ndv = '{}', '{}', '{}'".format(in_layer_path, in_layer_dtype))

        arr = arr[arr != ndv]
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

        return
