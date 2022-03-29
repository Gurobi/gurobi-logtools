from grblogtools import __version__, parse
from grblogtools.cli import cli

cli(
    glt_parse=parse,
    argparse_kwargs=dict(description="grblogtools " + __version__, prog="grblogtools"),
)
