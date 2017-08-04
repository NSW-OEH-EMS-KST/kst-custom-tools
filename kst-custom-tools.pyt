from contained_nearest_centroid import ContainedNearestCentroidTool
from sum_cost_distances import SumCostDistancesTool
from run_maxent import MaxentModellingTool
from single_feature_kml import SingleFeatureKmlTool
from percentiles import PercentilesTool
from pseudo_absence import PseudoRandomPointGenerator


class Toolbox(object):

    def __init__(self):

        self.label = "KST Custom Tools"
        self.alias = "kst_custom_toolbox"
        self.tools = [ContainedNearestCentroidTool, SumCostDistancesTool, MaxentModellingTool, SingleFeatureKmlTool, PercentilesTool, PseudoRandomPointGenerator]

        return

