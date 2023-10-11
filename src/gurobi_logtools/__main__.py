from gurobi_logtools import __version__, parse
from gurobi_logtools.cli import cli

cli(
    glt_parse=parse,
    argparse_kwargs=dict(
        description="gurobi-logtools " + __version__, prog="gurobi_logtools"
    ),
)
