import py_compile

ts = ["kst-custom-tools.pyt", "contained_nearest_centroid.py", "pseudo_point.py", "percentiles.py", "run_maxent.py", "single_feature_kml.py", "sum_cost_distances.py"]

for t in ts:
    py_compile.compile(t)
    print "compiled {}".format(t)

from contained_nearest_centroid import ContainedNearestCentroidTool
from sum_cost_distances import SumWeightedCostDistancesTool
from run_maxent import MaxentModellingTool
from single_feature_kml import SingleFeatureKmlTool
from percentiles import PercentilesTool
from pseudo_point import PseudoRandomAbsenceGenerator


class Toolbox(object):

    def __init__(self):

        self.tools = [ContainedNearestCentroidTool, SumWeightedCostDistancesTool, MaxentModellingTool, SingleFeatureKmlTool, PercentilesTool, PseudoRandomAbsenceGenerator]

        return


tb = Toolbox()
for t in tb.tools:
    try:
        tool = t()
        print "Executing {}".format(tool.label)
        tool.execute(tool.getParameterInfo(), None)
    except Exception as e:
        print e

