import argparse

import pandas as pd


def cli(glt_parse, argparse_kwargs):
    """Entry point function for command line interface

    Args:
        glt_parse: the parse function from grblogtools (in case overloads are needed)
        argparse_kwargs: extra info to pass to argparse

    """
    parser = argparse.ArgumentParser(**argparse_kwargs)
    parser.add_argument("outfile", help="Output file name (.xlsx)", metavar="XLSXFILE")
    parser.add_argument(
        "logfiles", help="Gurobi log files", nargs="+", metavar="LOGFILE"
    )
    parser.add_argument(
        "-t",
        "--timelines",
        action="store_true",
        help="also store timelines (root LP, node log, and NoRel log) in separate sheets",
    )
    args = parser.parse_args()

    result = glt_parse(args.logfiles)
    summary = result.summary()

    with pd.ExcelWriter(args.outfile) as writer:
        summary.to_excel(writer, sheet_name="Summary")
        for tl in ["norel", "rootlp", "nodelog"]:
            result.progress(tl).to_excel(writer, sheet_name=tl)

    print(f"extracted {len(summary)} log(s) to {args.outfile}")
