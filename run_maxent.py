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
import arcpy
import arcpy.mapping
import os
import sys
import csv
import subprocess
import collections


class MaxentModellingTool(object):

    def __init__(self):

        self.label = "Maxent Modelling"
        self.description = "Run 'Maxent' species distribution modelling tool"
        self.canRunInBackground = False
        self._parameters = None

        return

    # from maxent.jar...

    # public String[] getParameters()
    # {
    #     return new String[]
    #     {"responsecurves", "pictures", "jackknife", "outputformat", "outputfiletype", "outputdirectory", "projectionlayers", "samplesfile", "environmentallayers",
    #      "randomseed", "logscale", "warnings", "tooltips", "askoverwrite", "skipifexists", "removeduplicates", "writeclampgrid", "writemess", "randomtestpoints",
    #      "betamultiplier", "maximumbackground", "biasfile", "testsamplesfile", "replicates", "replicatetype", "perspeciesresults", "writebackgroundpredictions",
    #      "biasisbayesianprior", "responsecurvesexponent", "linear", "quadratic", "product", "threshold", "hinge", "polyhedral", "addsamplestobackground",
    #      "addallsamplestobackground", "autorun", "dosqrtcat", "writeplotdata", "fadebyclamping", "extrapolate", "visible", "autofeature", "givemaxaucestimate",
    #      "doclamp", "outputgrids", "plots", "appendtoresultsfile", "parallelupdatefrequency", "maximumiterations", "convergencethreshold", "adjustsampleradius",
    #      "threads", "lq2lqptthreshold", "l2lqthreshold", "hingethreshold", "beta_threshold", "beta_categorical", "beta_lqp", "beta_hinge", "biastype", "logfile",
    #      "scientificpattern", "cache", "cachefeatures", "defaultprevalence", "applythresholdrule", "togglelayertype", "togglespeciesselected",
    #      "togglelayerselected", "verbose", "allowpartialdata", "prefixes", "printversion", "nodata", "nceas", "factorbiasout", "priordistribution",
    #      "debiasaverages", "minclamping", "manualreplicates"};
    # }

    def getParameterInfo(self):

        jar = arcpy.Parameter(
            displayName="Maxent Runnable",
            name="jar",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        jar.filter.list = ["bat", "jar"]
        jar.value = locate_maxent_runnable()

        mem = arcpy.Parameter(
            displayName="Memory Commitment",
            name="mem",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        mem.filter.type = "Range"
        mem.filter.list = [512, 1024]
        mem.value = 512

        samplesfile = arcpy.Parameter(
            displayName="Samples File",
            name="samplesfile",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        samplesfile.filter.list = ["csv"]

        environmentallayers = arcpy.Parameter(
            displayName="Environmental Layers Directory",
            name="environmentallayers",
            datatype=["DEFolder"],
            parameterType="Required",
            direction="Input")

        outputdirectory = arcpy.Parameter(
            displayName="Output Directory",
            name="outputdirectory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        autorun = arcpy.Parameter(
            displayName="Run Automatically",
            name="autorun",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        autorun.value = True

        outputformat = arcpy.Parameter(
            displayName="Output Format",
            name="outputformat",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            category="Format")

        outputformat.filter.list = ["cloglog", "logistic", "cumulative", "raw"]
        outputformat.value = outputformat.filter.list[0]

        outputfiletype = arcpy.Parameter(
            displayName="Output File Type",
            name="outputfiletype",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            category="Format")

        outputfiletype.filter.list = ["asc", "mxe", "grd", "bil"]
        outputfiletype.value = outputfiletype.filter.list[0]

        projection_layers = arcpy.Parameter(
            displayName="Projection Layers Directory",
            name="projection_layers",
            datatype=["DEFile", "DEFolder"],
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        responsecurves = arcpy.Parameter(
            displayName="Create response curves",
            name="responsecurves",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        responsecurves.value = False

        pictures = arcpy.Parameter(
            displayName="Make pictures of predictions",
            name="pictures",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        pictures.value = True

        jacknife = arcpy.Parameter(
            displayName="Do jackknife to measure variable importance",
            name="jacknife",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        jacknife.value = False

        skip_existing = arcpy.Parameter(
            displayName="Skip if output exists",
            name="skipifexists",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        skip_existing.value = False

        warnings = arcpy.Parameter(
            displayName="Suppress warnings",
            name="warnings",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        warnings.value = False

        auto_features = arcpy.Parameter(
            displayName="Auto Features",
            name="auto_features",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        auto_features.value = True

        linear_features = arcpy.Parameter(
            displayName="Linear Features",
            name="linear_features",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        linear_features.value = True
        linear_features.enabled = False

        quadratic_features = arcpy.Parameter(
            displayName="Quadratic Features",
            name="quadratic_features",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        quadratic_features.value = True
        quadratic_features.enabled = False

        product_features = arcpy.Parameter(
            displayName="Product Features",
            name="product_features",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        product_features.value = True
        product_features.enabled = False

        threshold_features = arcpy.Parameter(
            displayName="Threshold Features",
            name="threshold_features",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        threshold_features.value = False
        threshold_features.enabled = False

        hinge_features = arcpy.Parameter(
            displayName="Hinge Features",
            name="hinge_features",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        hinge_features.value = False
        hinge_features.enabled = False

        verbose = arcpy.Parameter(
            displayName="Verbose Output",
            name="verbose",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
            category="Main Options")

        hinge_features.value = False

        return [jar, mem, samplesfile, environmentallayers, outputdirectory, autorun,
                outputformat, outputfiletype, projection_layers,
                responsecurves, pictures, jacknife, skip_existing, warnings,
                auto_features, linear_features, quadratic_features, product_features, threshold_features, hinge_features, verbose]

    def isLicensed(self):

        return True

    def updateParameters(self, parameters):

        # csv_param = get_parameter_by_name(parameters, "samplesfile")

        # if csv_param.altered:
        #     ds = None
        #     desc = arcpy.Describe(csv_param.valueAsText)
        #     try:
        #         ds = desc.dataSource
        #     except AttributeError:
        #         try:
        #             ds = desc.catalogPath
        #         except AttributeError:
        #             pass
        #     if ds:
        #         with open(ds, 'r') as f:
        #             rows = [row for row in csv.reader(f, delimiter=',')]
        #             unique_species = ";".join(list({row[0] for row in rows[1:]}))
        #
        #     species_param = get_parameter_by_name(parameters, "species")
        #     species_param.values = unique_species

        # enviro_layers_param = get_parameter_by_name(parameters, "environmentallayers")
        # enviro_param = get_by_name("enviro")
        #
        # if enviro_param.altered:
        #
        #     enviro_layers_param = get_by_name("environmentallayers")
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

        auto_features = get_parameter_by_name(parameters, "auto_features")

        if auto_features.altered:

            bool = [False, True][auto_features.valueAsText == "true"]

            enable_parameter_by_name(parameters, "linear_features", bool)
            enable_parameter_by_name(parameters, "quadratic_features", bool)
            enable_parameter_by_name(parameters, "product_features", bool)
            enable_parameter_by_name(parameters, "threshold_features", bool)
            enable_parameter_by_name(parameters, "hinge_features", bool)

        self.make_parameter_dict(parameters)

        return

    def updateMessages(self, parameters):

        return

    def make_parameter_dict(self, parameters):

        pd = collections.OrderedDict()
        for p in parameters:
            name = p.name
            if p.dataType == "Boolean":
                pd[name] = [False, True][p.valueAsText == "true"]
            elif p.dataType == "Double":
                pd[name] = float(p.valueAsText) if p.valueAsText else None
            elif p.dataType == "Long":
                pd[name] = int(float(p.valueAsText)) if p.valueAsText else None
            else:
                pd[name] = p.valueAsText

        # try:
        #     desc = arcpy.Describe(pd["samplesfile"])
        #     try:
        #         ds = desc.dataSource
        #     except AttributeError:
        #         try:
        #             ds = desc.catalogPath
        #         except AttributeError:
        #             ds = None
        # except:
        #     ds = None
        #
        # pd["samplesfile"] = ds

        self._parameters = pd

        pd["summary"] = ", ".join(["{}: {}".format(k, v) for k, v in self._parameters.iteritems()])

        self._parameters = pd

        return

    def execute(self, parameters, messages):

        self.make_parameter_dict(parameters)

        messages.addMessage("")
        messages.addMessage("Parameter Summary: {}".format(self._parameters["summary"]))

        cmdargs = build_commands(self._parameters)
        cmdstr = " ".join(cmdargs)

        messages.addMessage("")
        messages.addMessage("Starting Maxent with command line:")
        messages.addMessage(cmdstr)

        process = subprocess.Popen(cmdstr, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # can't get working with shell=False and cmdargs = [...]
        stdout, stderr = process.communicate()
        retcode = process.returncode
        retstr = "Return Code {}".format(retcode)

        messages.addMessage("")
        if not retcode:
             messages.addMessage(retstr + " Success")
        else:
            messages.addMessage(retstr + " Failure")

        messages.addMessage("")
        messages.addMessage("stdout:")
        messages.addMessage(stdout)
        messages.addMessage("")
        messages.addMessage("stderr:")
        messages.addMessage(stderr)

        out_dir = self._parameters["outputdirectory"]

        log = os.path.join(out_dir, "maxent.log")
        messages.addMessage("")
        if not os.path.exists(log):
            messages.addMessage("{} not found".format(log))
        else:
            messages.addMessage("Log contents:")
            for line in list(open(log)):
                line = line.strip()
                if line:
                    messages.addMessage(line)

        out_fmt = self._parameters["outputfiletype"]
        out_files = [fn for fn in os.listdir(out_dir) if fn.endswith(out_fmt)]
        out_files = [os.path.join(out_dir, fn) for fn in out_files]

        messages.addMessage("")
        messages.addMessage("Result files generated:")
        for fn in out_files:
            messages.addMessage(fn)

        messages.addMessage("")
        messages.addMessage("Adding output to map")
        for fn in out_files:
            mxd = arcpy.mapping.MapDocument("CURRENT")
            df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
            newlayer = arcpy.mapping.Layer(fn)
            try:
                arcpy.mapping.AddLayer(df, newlayer, "BOTTOM")
                messages.addMessage("{} added".format(fn))
            except Exception as e:
                messages.addMessage("Could not add {} added".format(e))

        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()

        return


def locate_maxent_runnable():

    script_path = sys.path[0]
    jar = os.path.join(script_path, "maxent", "maxent.jar")

    if os.path.exists(jar):
        return jar

    return "not found at {}".format(jar)


def get_parameter_by_name(parameters, parameter_name):

    for param in parameters:
        if param.name == parameter_name:
            return param

    raise ValueError("Parameter '{}' not found".format(parameter_name))


def set_parameter_by_name(parameters, parameter_name, value):

    param = get_parameter_by_name(parameters, parameter_name)
    param.value = value

    return


def enable_parameter_by_name(parameters, parameter_name, value):

    param = get_parameter_by_name(parameters, parameter_name)
    param.enabled = value

    return


def build_commands(pars):

    cmd = 'java'

    cmd += ' -mx{}m'.format(pars['mem'])

    cmd += ' -jar "{}"'.format(pars['jar'])

    cmd += ' samplesfile="{}"'.format(pars['samplesfile'])

    cmd += ' environmentallayers="{}"'.format(pars['environmentallayers'])

    cmd += ' outputdirectory="{}"'.format(pars['outputdirectory'])

    cmd += ' outputformat={}'.format(pars['outputformat'])

    cmd += ' outputfiletype={}'.format(pars['outputfiletype'])

    cmd += ['', ' responsecurves'][pars['responsecurves']]

    cmd += ['', ' pictures'][pars['pictures']]

    cmd += ['', ' jackknife'][pars['jacknife']]

    cmd += ['', ' skipifexists'][pars['skipifexists']]

    cmd += ['', ' warnings'][pars['warnings']]

    cmd += ['', ' autorun'][pars['autorun']]

    cmd += ['', ' verbose'][pars['verbose']]

    return cmd.split()


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
