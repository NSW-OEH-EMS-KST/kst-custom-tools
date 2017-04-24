#
#-------------------------------------------------------------
# Name:       RunMaxentModel.py
# Purpose:    Runs a Maxent model using Stephen Phillips'
#             javascript Maxent application
# Author:     John Donoghue II (mail@johndonoghue.net)
# Created:    18/02/2013
# Copyright:   John Donoghue II
# ArcGIS Version:   10
# Python Version:   2.6
#-------------------------------------------------------------
#

# import arcpy, os, csv
#
# # get the location to the maxent jar file
# maxent = arcpy.GetParameterAsText(0)

# # Get the csv file to model
# csvFile = arcpy.GetParameterAsText(1)

# # get the name of the folder containing the bioclimatic data
# climatedataFolder = arcpy.GetParameterAsText(2)

# # get the name of the folder to save the Maxent model results to
# outputFolder = arcpy.GetParameterAsText(3)

# # get the type of model to generate
# optOutputFormat = arcpy.GetParameterAsText(4)

# # get the type of output file to save
# optOutputFileType = arcpy.GetParameterAsText(5)

# # get options
# optResponseCurves= arcpy.GetParameterAsText(6)
# optPredictionPictures = arcpy.GetParameterAsText(7)
# optJackknife = arcpy.GetParameterAsText(8)
# optSkipifExists = arcpy.GetParameterAsText(9)
# supressWarnings = arcpy.GetParameterAsText(10)





# # get name of species from input file
# species = os.path.basename(csvFile)
# species = species[1:-4]
#
# # create a folder for each species
# newOutputFolder = outputFolder + "\\""" + species
# if os.path.isdir(newOutputFolder):
#     arcpy.AddMessage(" ")
# else:
#     os.mkdir(newOutputFolder)
#
# # or write a separate maxent results file for each species
# "perspeciesresults=true"
#
# # create the maxent command
# myCommand = "java -mx512m -jar \"" + maxent + "\" -e \"" + climatedataFolder + "\""
# myCommand += " -s \"" + csvFile + "\" -o \"" + newOutputFolder + "\""
# myCommand += " outputformat=" + optOutputFormat.lower() + " outputfiletype=" + optOutputFileType.lower()
#
# # add options
# if optResponseCurves == 'true':
#     myCommand += " -P"
# if optPredictionPictures == 'true':
#     myCommand += " pictures=true"
# else:
#     myCommand += " pictures=false"
# if optJackknife  == 'true':
#     myCommand += " -J"
# if optSkipifExists  == 'true':
#     myCommand += " -S"
# if supressWarnings  == 'true':
#     myCommand += " warnings=false"
# else:
#     myCommand += " warnings=true"
#
# # finish the command
# myCommand += " -a"
#
# # add a message
# arcpy.AddMessage("Starting Maxent")
# arcpy.AddMessage(myCommand)
#
# # execute the command
# result = os.system(myCommand)
#
# if (result == 0):
#     arcpy.AddMessage(" ")
#     arcpy.AddMessage("Finished")
# else:
#     arcpy.AddMessage(" ")
#     arcpy.AddError("Error Running Maxent")

import arcpy
import os
from collections import OrderedDict


class RunMaxentTool(object):

    def __init__(self):

        self.label = "Run Maxent"
        self.description = "Runs Maxent"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="MaxEnt JAR File",
            name="jar_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        param0.filter.list = ["*.jar"]

        param1 = arcpy.Parameter(
            displayName="?? CSV File",
            name="csv_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        param1.filter.list = ["*.csv"]

        param2 = arcpy.Parameter(
            displayName="?? Climate Data Folder",
            name="climate_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Output Model Type",
            name="out_model_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param3.filter.list = ["Logistic", "Cumulative", "Raw"]

        param4 = arcpy.Parameter(
            displayName="Output File Format",
            name="out_file_format",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param4.filter.list = ["asc", "mxe", "grd", "bil"]

        param5 = arcpy.Parameter(
            displayName="Output Workspace",
            name="out_folder",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Create prediction curves",
            name="create_prediction_curves",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        param6.value = False

        param7 = arcpy.Parameter(
            displayName="Create response curves",
            name="create_response_curves",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        param7.value = True

        param8 = arcpy.Parameter(
            displayName="Do jacknife to measure variable importance",
            name="do_jacknife",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        param8.value = True

        param9 = arcpy.Parameter(
            displayName="Skip if output exists",
            name="skip_if_exists",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        param9.value = False

        param10 = arcpy.Parameter(
            displayName="Suppress warnings",
            name="suppress_warnings",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        param10.value = False

        return [param0, param1, param2, param3, param4, param5, param6, param8, param9, param10]

    def isLicensed(self):

        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):

        # parameter_dictionary = OrderedDict([(p.DisplayName, p.valueAsText) for p in parameters])
        # parameter_summary = ", ".join(["{}: {}".format(k, v) for k, v in parameter_dictionary.iteritems()])
        messages.addMessage("Not Implemented")

        # features, features_fieldname, cost_raster, max_cost_distance, out_raster_cellsize, out_ws, delete_costs = parameter_dictionary.values()
        #
        # try:
        #     arcpy.SelectLayerByAttribute_management(features, "CLEAR_SELECTION")
        #     messages.addMessage("Selection in layer '{}' cleared".format(features))
        # except:
        #     pass
        #
        # unique_values = sorted({row[0] for row in arcpy.da.SearchCursor(features, features_fieldname) if row[0]})
        # unique_values_count = len(unique_values)
        # messages.addMessage("The feature dataset field '{}' has {} unique values: {}".format(features_fieldname, unique_values_count, unique_values))
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
        #     where = '"{}" = {}'.format(features_fieldname, value)
        #     arcpy.SelectLayerByAttribute_management(features, "NEW_SELECTION", where)
        #     try:
        #         cost = arcpy.sa.CostDistance(features, cost_raster, max_cost_distance)
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
        # sum_raster.save(make_output_name("cost_sum", out_ws))
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
        #     arcpy.SelectLayerByAttribute_management(features, "CLEAR_SELECTION")
        # except:
        #     pass


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
