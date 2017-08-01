from __future__ import print_function
import arcpy
import os
from datetime import datetime
from collections import OrderedDict
from random import random
from math import sqrt, pi, cos, sin
import logging
import logging.handlers

MAX_ITS = 100000


class PseudoAbsenceGenerator(object):

    def __init__(self):

        self.label = "Pseudo-absence Generator"
        self.description = "Generate a pseudo-absence layer"
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        param0 = arcpy.Parameter(
            displayName="Sample Points Layer",
            name="in_sample_points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param0.filter.list = ["Point"]

        param1 = arcpy.Parameter(
            displayName="Point Features ID Field",
            name="in_points_id_field",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        param1.parameterDependencies = ["in_sample_points"]

        param2 = arcpy.Parameter(
            displayName="Maximum Offset",
            name="in_offset_max",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Minimum Offset",
            name="in_offset_min",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Study Area",
            name="in_study_layer",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input")

        param4.filter.list = ["Polygon"]

        param5 = arcpy.Parameter(
            displayName="Proximity Layer",
            name="in_proximity_layer",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Minimum Proximity",
            name="in_proximity_min",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Output Workspace",
            name="in_out_ws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param7.defaultEnvironmentName = "workspace"

        param8 = arcpy.Parameter(
            displayName="Output Layer Name",
            name="in_out_lyr",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param9 = arcpy.Parameter(
            displayName="Maximum Iterations",
            name="max_its",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        param9.value = MAX_ITS

        param10 = arcpy.Parameter(
            displayName="Pseudo Points",
            name="out_pt_lyr",
            datatype="GPLayer",
            parameterType="Derived",
            direction="Output")

        param11 = arcpy.Parameter(
            displayName="Study Points",
            name="out_study_pts",
            datatype="GPLayer",
            parameterType="Derived",
            direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11]

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

        add_message = messages.addMessage
        logger = init_log(add_message)

        parameter_dictionary = OrderedDict([(p.DisplayName, p.valueAsText) for p in parameters[:-2]])
        add_message("Parameter summary:")
        [add_message("{}: {}".format(k, v)) for k, v in parameter_dictionary.iteritems()]

        add_message(parameter_dictionary.values())

        in_sample_points, in_points_id_field, in_offset_max, in_offset_min, \
        in_study_layer, in_proximity_layer, in_proximity_min, \
        in_out_ws, in_out_lyr, max_its = parameter_dictionary.values()

        global MAX_ITS
        MAX_ITS = float(max_its)

        # cast inputs to float
        in_offset_max = float(in_offset_max) if in_offset_max not in [None, "#"] else 0
        in_offset_min = float(in_offset_min) if in_offset_min not in [None, "#"] else 0
        in_proximity_min = float(in_proximity_min) if in_proximity_min not in [None, "#"] else 0

        # delete existing data
        out_name = os.path.join(in_out_ws, in_out_lyr)
        if arcpy.Exists(out_name):
            arcpy.Delete_management(out_name)
            add_message("Existing '{}' deleted".format(out_name))

        # Get spatial reference object from sample point layer and create a new empty feature class
        spat_ref = arcpy.Describe(in_sample_points).SpatialReference
        arcpy.CreateFeatureclass_management(in_out_ws, in_out_lyr, "POINT", spatial_reference=spat_ref)
        arcpy.AddField_management(out_name, "parent_id", "TEXT", field_length=255)
        arcpy.AddField_management(out_name, "xy_orig", "TEXT", field_length=255)
        arcpy.AddField_management(out_name, "xy_pseudo", "TEXT", field_length=255)
        arcpy.AddField_management(out_name, "iterations", "TEXT", field_length=255)
        arcpy.AddField_management(out_name, "duration", "TEXT", field_length=255)
        arcpy.AddField_management(out_name, "status", "TEXT", field_length=255)
        add_message("Point dataset '{}' created".format(out_name))

        # make the sample points layer
        arcpy.MakeFeatureLayer_management(in_sample_points, "points_layer")
        total_points = int(arcpy.GetCount_management("points_layer").getOutput(0))
        add_message("Points layer contains {} features in total".format(total_points))

        # select features if study area provided
        if in_study_layer:
            arcpy.MakeFeatureLayer_management(in_study_layer, "study_layer")
            total_feats = int(arcpy.GetCount_management("study_layer").getOutput(0))
            add_message("Study layer contains {} feature(s)".format(total_feats, in_study_layer))

            arcpy.SelectLayerByLocation_management("points_layer", "WITHIN", "study_layer")  #, {search_distance}, {selection_type}, {invert_spatial_relationship})
            study_points = os.path.join(in_out_ws, in_out_lyr + "_study_points")
            arcpy.CopyFeatures_management("points_layer", study_points)

            study_point_count = int(arcpy.GetCount_management("points_layer").getOutput(0))
            add_message("Points layer contains {} features within study area '{}'".format(study_point_count, in_study_layer))
            study_feats = [f[0] for f in arcpy.da.SearchCursor("study_layer", ["SHAPE@"])]
        else:
            study_feats = []

        add_message("study features: {}".format(study_feats))

        # if proximity layer provided, select features
        if in_proximity_layer and in_proximity_min:
            arcpy.MakeFeatureLayer_management(in_proximity_layer, "proximity_layer")
            total_feats = int(arcpy.GetCount_management("proximity_layer").getOutput(0))
            add_message("Proximity layer contains {} features in total".format(total_feats, in_study_layer))
            if in_study_layer:
                arcpy.SelectLayerByLocation_management("proximity_layer", "WITHIN", "study_layer")  # , {search_distance}, {selection_type}, {invert_spatial_relationship})
                total_feats = int(arcpy.GetCount_management("proximity_layer").getOutput(0))
                add_message("Proximity layer contains {} features within study area '{}'".format(total_feats, in_study_layer))
            proximity_feats = [f[0] for f in arcpy.da.SearchCursor(in_proximity_layer, ["SHAPE@"])[0]]
        else:
            proximity_feats = []

        add_message("proximity features: {}".format(proximity_feats))

        add_message("Generating pseudo-points...")

        # get the points in a cursor
        point_rows = arcpy.da.SearchCursor("points_layer", ['SHAPE@', in_points_id_field])

        result = []
        row_num = 0
        for point_row in point_rows:

            point = point_row[0].centroid
            point_id = point_row[1]
            row_num += 1

            x = [point_id]  # , "x={} y={}".format(point.X, point.Y)]
            x.extend(generate_pseudo_point(point, in_offset_max, in_offset_min, study_feats, proximity_feats, in_proximity_min, logger.debug))
            add_message("Pseudo-random point {} : old ({})  new ({}) : took {} iterations, {} seconds : ".format(*x))  # id, xy, n, t, s, xy
            result.append(x)

        with arcpy.da.InsertCursor(out_name, ["parent_id", "xy_orig", "xy_pseudo", "iterations", "duration", "status", "SHAPE@XY"]) as ICur:
            for v in result:
                add_message(v)
                ICur.insertRow(v)  # insert it into the feature class

        arcpy.SetParameterAsText(10, out_name)
        arcpy.SetParameterAsText(11, study_points if in_study_layer else in_sample_points)

        return


def generate_pseudo_point(point, max_offset, min_offset=0, study_features=[], proximity_features=[], min_proximity_offset=0, print_func=print):

    # print_func(locals())

    n, unsolved = 0, True
    start = datetime.now()

    xy = "{}, {}".format(point.X, point.Y)

    while unsolved:
        if n > MAX_ITS:
            return xy, "{}, {}".format(-9999, -9999), n-1, str(datetime.now() - start), "max iterations reached {}".format(MAX_ITS), (-9999, -9999)

        n += 1

        u = random()
        v = random()

        w = max_offset * sqrt(u)
        t = 2.0 * pi * v
        x = point.X + w * cos(t)
        y = point.Y + w * sin(t)

        if min_offset:
            if sqrt((x - point.X)**2 + (y - point.Y)**2) < min_offset:
                print_func("too close to original")
                # REJECTED
                continue

        point.X, point.Y = x, y  # RE-USING POINT OBJECT ********************

        # is point within study area
        if study_features:
            for s in study_features:  # is point within study area
                if not point.within(s):
                    # REJECTED
                    continue

        # is point too close to proximity features
        if proximity_features and min_proximity_offset:  # is point too close to proximity layer
            for p in proximity_features:
                if point.distanceTo(p) < min_proximity_offset:
                    print_func("too close to proximity feature")
                    # REJECTED
                    continue

        unsolved = False

    return xy, "{}, {}".format(point.X, point.Y), n, str(datetime.now() - start), "solved", (point.X, point.Y)  # xy


def init_log(print_func=print):

    log_filename = 'pseudo-absences.log'

    logger = logging.getLogger('pseudo-absence')
    logger.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(log_filename, maxBytes=2000000, backupCount=5)

    logger.addHandler(handler)

    filename = handler.baseFilename

    print_func("Logging file at {}".format(filename))

    return logger
