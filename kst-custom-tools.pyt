import arcpy
from contained_nearest_centroid import ContainedNearestCentroidTool
from sum_cost_distances import SumCostDistancesTool
from run_maxent import MaxentModellingTool


class Toolbox(object):

    def __init__(self):

        self.label = "KST Custom Tools"
        self.alias = "kst_custom_toolbox"
        self.tools = [ContainedNearestCentroidTool, SumCostDistancesTool, MaxentModellingTool]

        return

