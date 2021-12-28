from . import __version__, get_dataframe
from .cli import cli

cli(
    get_dataframe=get_dataframe,
    argparse_kwargs=dict(description="grblogtools " + __version__, prog="grblogtools"),
)
