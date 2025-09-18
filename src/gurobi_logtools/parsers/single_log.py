from gurobi_logtools.parsers.multiobj import MultiObjParser
from gurobi_logtools.parsers.single_log_base import SingleLogBase


class SingleLogParser(SingleLogBase):
    """This class parses one single log file.

    It expects parse to be called once for each line in a log file.
    """

    _MultiObjParser = MultiObjParser

    def get_multiobj_summary(self):
        return self.multiobj_parser.get_objn_summaries()
