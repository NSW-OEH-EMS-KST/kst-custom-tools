from __future__ import print_function
import arcpy
import os
from datetime import datetime
from collections import OrderedDict
from random import random
from math import sqrt, pi, cos, sin


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
            displayName="Output Layer",
            name="out_pt_lyr",
            datatype="GPLayer",
            parameterType="Derived",
            direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9]

    def isLicensed(self):

        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):

        add_message = messages.addMessage

        parameter_dictionary = OrderedDict([(p.DisplayName, p.valueAsText) for p in parameters[:-1]])
        parameter_summary = ", ".join(["{}: {}".format(k, v) for k, v in parameter_dictionary.iteritems()])
        add_message("Parameter summary: {}".format(parameter_summary))

        in_sample_points, in_points_id_field, in_offset_max, in_offset_min, \
        in_study_layer, in_proximity_layer, in_proximity_min, \
        in_out_ws, in_out_lyr = parameter_dictionary.values()

        # cast inputs to float
        in_offset_max = float(in_offset_max) if in_offset_max not in [None, "#"] else 0
        in_offset_min = float(in_offset_min) if in_offset_min not in [None, "#"] else 0
        in_proximity_min = float(in_proximity_min) if in_proximity_min not in [None, "#"] else 0
        # for i in [in_offset_max, in_offset_min, in_proximity_min]:
        #     i = float(i) if i not in [None, "#"] else None
        #     add_message(i)
        add_message("{} {} {}".format(in_offset_min, in_offset_max, in_proximity_min))
        add_message("{} {} {}".format(type(in_offset_min), type(in_offset_max), type(in_proximity_min)))
        total_points = int(arcpy.GetCount_management(in_sample_points).getOutput(0))
        add_message("Points layer contains {} features".format(total_points))

        # delete existing data
        out_name = os.path.join(in_out_ws, in_out_lyr)
        if arcpy.Exists(out_name):
            arcpy.Delete_management(out_name)
            add_message("Existing '{}' deleted".format(out_name))

        # Get spatial reference object from sample point layer and create a new empty feature class
        spat_ref = arcpy.Describe(in_sample_points).SpatialReference
        arcpy.CreateFeatureclass_management(in_out_ws, in_out_lyr, "POINT", spatial_reference=spat_ref)
        arcpy.AddField_management(out_name, "parent_id", "TEXT", field_length=255)
        arcpy.AddField_management(out_name, "xy", "TEXT", field_length=255)
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
            study_points = int(arcpy.GetCount_management("points_layer").getOutput(0))
            add_message("Points layer contains {} features within study area '{}'".format(study_points, in_study_layer))
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

        # get the points in a cursor
        point_rows = arcpy.da.SearchCursor("points_layer", ['SHAPE@XY', in_points_id_field])

        result = []
        row_num = 0
        for point_row in point_rows:

            x0, y0 = point_row[0]
            point_id = point_row[1]

            row_num += 1

            x = [point_id]
            x.extend(generate_pseudo_point(x0, y0, in_offset_max, in_offset_min, study_feats, proximity_feats, in_proximity_min, add_message))
            add_message("Pseudo-random point {}: {} : took {} iterations, {} seconds".format(*x))  # id, xy, n, t, xy
            result.append(x)

        with arcpy.da.InsertCursor(out_name, ["parent_id", "xy", "iterations", "duration", "SHAPE@XY"]) as ICur:
            for v in result:
                ICur.insertRow(v)  # insert it into the feature class

        arcpy.SetParameterAsText(9, out_name)

        return


def generate_pseudo_point(x0, y0, max_offset, min_offset=0, study_features=[], proximity_features=[], min_proximity_offset=0, print_func=print):

    n, max_it = 0, 10000
    start = datetime.now()
    while True:
        n += 1

        if n > max_it:
            return "-9999, -9999", 0, 0, "max iterations reached {}".format(max_it), "-9999, -9999"

        u = random()
        v = random()

        w = max_offset * sqrt(u)
        t = 2.0 * pi * v
        x = x0 + w * cos(t)
        y = y0 + w * sin(t)

        if min_offset:
            if sqrt((x - x0)**2 + (y - y0)**2) < min_offset:
                print_func("too close to original")
                continue

        # is point within study area
        p = arcpy.Point()
        p.X, p.Y = x, y
        if study_features:
            if True not in [p.within(f) for f in study_features]:
                print_func("not within study feature")
                # if True not in list(map(p.within, study_features)):
                continue

        # is point too close to proximity layer
        if proximity_features:
            if min([p.distanceTo(f) for f in study_features]) < min_proximity_offset:
                print_func("too close to proximity feature")
                # if min(map(p.distanceTo, proximity_features)) < min_proximity_offset:
                continue

        # if we got here, we are good
        t = datetime.now() - start
        xy = "{}, {}".format(x, y)
        return xy, n, t, "ok", xy
