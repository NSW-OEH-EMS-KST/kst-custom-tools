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
import sys
from collections import OrderedDict


class MaxentModellingTool(object):

    def __init__(self):

        self.label = "Maxent Modelling"
        self.description = "Run 'Maxent' species distribution modelling tool"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        runnable = arcpy.Parameter(
            displayName="Maxent Runnable",
            name="run_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        runnable.filter.list = ["bat", "jar"]
        runnable.value = locate_maxent_runnable()

        samples = arcpy.Parameter(
            displayName="Samples File(s)",
            name="csv_files",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        samples.filter.list = ["*.csv"]

        enviro = arcpy.Parameter(
            displayName="Environmental Layers Directory",
            name="climate_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        out_dir = arcpy.Parameter(
            displayName="Output Directory",
            name="out_dir",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        model_type = arcpy.Parameter(
            displayName="Output Model Type",
            name="out_model_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        model_type.filter.list = ["Logistic", "Cumulative", "Raw"]
        model_type.value = model_type.filter.list[0]

        out_format = arcpy.Parameter(
            displayName="Output File Format",
            name="out_file_format",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        out_format.filter.list = ["asc", "mxe", "grd", "bil"]
        out_format.value = out_format.filter.list[0]

        create_response = arcpy.Parameter(
            displayName="Create response curves",
            name="create_response_curves",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        create_response.value = False

        make_pictures = arcpy.Parameter(
            displayName="Make pictures of predictions",
            name="make_prediction_pictures",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        make_pictures.value = True

        do_jacknife = arcpy.Parameter(
            displayName="Do jackknife to measure variable importance",
            name="do_jacknife",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        do_jacknife.value = False

        skip_existing = arcpy.Parameter(
            displayName="Skip if output exists",
            name="skip_if_exists",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        skip_existing.value = False

        suppress_warnings = arcpy.Parameter(
            displayName="Suppress warnings",
            name="suppress_warnings",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        suppress_warnings.value = False

        return [runnable, samples, enviro, out_dir, model_type, out_format, create_response, do_jacknife, skip_existing, suppress_warnings]

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


def locate_maxent_runnable():
    script_path = sys.path[0]
    bat = os.path.join(script_path, "maxent", "maxent.bat")
    jar = os.path.join(script_path, "maxent", "maxent.jar")
    print bat, jar

    if os.path.exists(bat):
        return bat
    elif os.path.exists(jar):
        return jar

    return "not found"

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
