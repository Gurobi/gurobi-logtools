from .cli import cli
from . import get_dataframe, __version__

cli(
    get_dataframe=get_dataframe,
    argparse_kwargs=dict(description="grblogtools " + __version__, prog="grblogtools"),
)
