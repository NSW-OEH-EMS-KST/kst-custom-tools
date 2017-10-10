from contained_nearest_centroid import ContainedNearestCentroidTool
from sum_cost_distances import SumWeightedCostDistancesTool
from run_maxent import MaxentModellingTool
from single_feature_kml import SingleFeatureKmlTool
from percentiles import PercentilesTool
from pseudo_point import PseudoRandomAbsenceGenerator


class Toolbox(object):

    def __init__(self):

        self.label = "KST Custom Tools"
        self.alias = "kst_custom_toolbox"
        self.tools = [ContainedNearestCentroidTool, SumWeightedCostDistancesTool, MaxentModellingTool, SingleFeatureKmlTool, PercentilesTool, PseudoRandomAbsenceGenerator]

        return

