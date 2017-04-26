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
import csv
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

        samples_csv = arcpy.Parameter(
            displayName="Samples File",
            name="samples_csv",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input")

        # samples_csv.filter.list = ["csv"]

        species = arcpy.Parameter(
            displayName="Species",
            name="species",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        enviro_layers = arcpy.Parameter(
            displayName="Environmental Layers",
            name="enviro_layers",
            datatype=["GPRasterLayer", "DERasterDataset"],
            parameterType="Required",
            direction="Input",
            multiValue=True)
        #
        # enviro.filter.list = ["csv", "asc"]

        enviro_layers_type = arcpy.Parameter(
            displayName="Environmental Layers Types",
            name="enviro_layers_type",
            datatype="GPValueTable",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        enviro_layers_type.columns = [["GPString", "Layer"], ["GPString", "Type"]]
        enviro_layers_type.filters[1].type = "ValueList"
        enviro_layers_type.filters[1].list = ["Continuous", "Categorical"]

        out_dir = arcpy.Parameter(
            displayName="Output Directory",
            name="out_dir",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        model_type = arcpy.Parameter(
            displayName="Output Model Type",
            name="model_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            category="Format")

        model_type.filter.list = ["Logistic", "Cumulative", "Raw"]
        model_type.value = model_type.filter.list[0]

        out_format = arcpy.Parameter(
            displayName="Output File Format",
            name="out_format",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            category="Format")

        out_format.filter.list = ["asc", "mxe", "grd", "bil"]
        out_format.value = out_format.filter.list[0]

        projection_layers = arcpy.Parameter(
            displayName="Projection Layers",
            name="projection_layers",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            category="Format")

        projection_layers.filter.list = ["asc", "mxe", "grd", "bil"]
        projection_layers.value = out_format.filter.list[0]

        create_response = arcpy.Parameter(
            displayName="Create response curves",
            name="create_response_curves",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        create_response.value = False

        make_pictures = arcpy.Parameter(
            displayName="Make pictures of predictions",
            name="make_prediction_pictures",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        make_pictures.value = True

        do_jacknife = arcpy.Parameter(
            displayName="Do jackknife to measure variable importance",
            name="do_jacknife",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        do_jacknife.value = False

        skip_existing = arcpy.Parameter(
            displayName="Skip if output exists",
            name="skip_if_exists",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        skip_existing.value = False

        suppress_warnings = arcpy.Parameter(
            displayName="Suppress warnings",
            name="suppress_warnings",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        suppress_warnings.value = False

        auto_features = arcpy.Parameter(
            displayName="Auto Features",
            name="auto_features",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        auto_features.value = True

        linear_features = arcpy.Parameter(
            displayName="Linear Features",
            name="linear_features",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        linear_features.value = True

        quadratic_features = arcpy.Parameter(
            displayName="Quadratic Features",
            name="quadratic_features",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        quadratic_features.value = True

        product_features = arcpy.Parameter(
            displayName="Product Features",
            name="product_features",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        product_features.value = True

        threshold_features = arcpy.Parameter(
            displayName="Threshold Features",
            name="threshold_features",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        threshold_features.value = False

        hinge_features = arcpy.Parameter(
            displayName="Hinge Features",
            name="hinge_features",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
            category="Options")

        hinge_features.value = False

        return [runnable, samples_csv, species, enviro_layers, enviro_layers_type, out_dir,
                model_type, out_format, projection_layers,
                create_response, make_pictures, do_jacknife, skip_existing, suppress_warnings,
                auto_features, linear_features, quadratic_features, product_features, threshold_features, hinge_features]

    def isLicensed(self):

        return True

    def updateParameters(self, parameters):

        def get_by_name(parameter_name):
            for param in parameters:
                if param.name == parameter_name:
                    return param
            raise ValueError("Parameter '{}' not found".format(p))

        def set_by_name(parameter_name, value):
            param = get_by_name(parameter_name)
            param.value = value
            return

        csv_param = get_by_name("samples_csv")

        if csv_param.altered:

            with open(csv_param.valueAsText, 'r') as f:
                rows = [row for row in csv.reader(f, delimiter=',')]
                unique_species = ";".join(list({row[0] for row in rows[1:]}))

            species_param = get_by_name("species")
            species_param.values = unique_species

        enviro_layers_param = get_by_name("enviro_layers")
        # enviro_param = get_by_name("enviro")
        #
        # if enviro_param.altered:
        #
        #     enviro_layers_param = get_by_name("enviro_layers")
        #
        #     enviro_values = enviro_param.valueAsText
        #     if not enviro_values:
        #         enviro_layers_param.values = None
        #     else:
        #         layer_values = enviro_layers_param.valueAsText
        #         if layer_values:
        #             layer_values = layer_values.split(";")
        #         if enviro_values:
        #         enviro_values = enviro_values.split(";")
        #         enviro_layers_param.values = [[lyr, typ] for lyr, typ in  ]
        #     else:
        #         enviro_layers_param.values = []
        #
        #
        #     layer_values = enviro_layers_param.valueAsText
        #     if layer_values:
        #         layer_values = layer_values.split(";")
        #         for lyr in enviro_values:
        #     else:
        #         layer_values = []
        #     value = enviro_param.valueAsText
        #     value_type = arcpy.Describe(value).dataType
        #     print value_type
        #     if value_type == "Folder":
        #         files = [f for f in os.listdir(value) if f.endswith(tuple(".asc"))]
        #         layer_values.append([[f, "Continuous"]] for f in files)
        #     elif value_type == "File":
        #         if value.endswith([".csv", ".asc"]):
        #             layer_values.append([value, "Continuous"])
        #     # else:
        #     #     print "invalid"
        #     enviro_layers_param.values = layer_values

            # with open(csv_param.valueAsText, 'r') as f:
            #     rows = [row for row in csv.reader(f, delimiter=',')]
            #     unique_species = ";".join(list({row[0] for row in rows[1:]}))
            #
            # species_param.values = unique_species

        auto_features = get_by_name("auto_features")

        if auto_features.altered:

            bool = [False, True][auto_features == "true"]

            set_by_name("linear_features", bool)
            set_by_name("linear_features", bool)
            set_by_name("quadratic_features", bool)
            set_by_name("product_features", bool)
            set_by_name("threshold_features", bool)
            set_by_name("hinge_features", bool)

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):

        parameter_dictionary = OrderedDict([(p.DisplayName, p.valueAsText) for p in parameters])
        parameter_summary = ", ".join(["{}: {}".format(k, v) for k, v in parameter_dictionary.iteritems()])
        messages.addMessage("Parameter Summary:\n" + parameter_summary)
        messages.addMessage("Nothing else implemented")


def locate_maxent_runnable():

    script_path = sys.path[0]
    bat = os.path.join(script_path, "maxent", "maxent.bat")
    jar = os.path.join(script_path, "maxent", "maxent.jar")

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
