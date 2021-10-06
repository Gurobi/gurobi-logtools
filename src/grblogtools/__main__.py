import argparse
import grblogtools as glt
import pandas as pd

parser = argparse.ArgumentParser(
    description="grblogtools " + glt.__version__, prog="grblogtools"
)
parser.add_argument("outfile", help="Output file name (.xlsx)", metavar="XLSXFILE")
parser.add_argument("logfiles", help="Gurobi log files", nargs="+", metavar="LOGFILE")
parser.add_argument(
    "-t",
    "--timelines",
    action="store_true",
    help="also store timelines (root LP, node log, and NoRel log) in separate sheets",
)
parser.add_argument(
    "-m",
    "--mergedlogs",
    action="store_true",
    help="log files contain multiple logs to be extracted",
)
args = parser.parse_args()

if args.timelines:
    summary, timelines = glt.get_dataframe(
        args.logfiles, timelines=True, merged_logs=args.mergedlogs
    )
    with pd.ExcelWriter(args.outfile) as writer:
        summary.to_excel(writer, sheet_name="Summary")
        for tl in timelines:
            timelines[tl].to_excel(writer, sheet_name=tl)
else:
    summary = glt.get_dataframe(args.logfiles, merged_logs=args.mergedlogs)
    with pd.ExcelWriter(args.outfile) as writer:
        summary.to_excel(writer, sheet_name="Summary")

print(f"extracted {len(summary)} log(s) to {args.outfile}")
