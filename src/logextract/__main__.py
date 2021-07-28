import argparse
import xlsxwriter
import logextract as lx

parser = argparse.ArgumentParser(description="Gurobi Log File Information Extractor.")
parser.add_argument("outfile", help="Output file name (.xlsx)", metavar="XLSXFILE")
parser.add_argument(
    "logfiles", help="Gurobi Optimizer log files", nargs="+", metavar="LOGFILE"
)
args = parser.parse_args()

wb = xlsxwriter.Workbook(args.outfile, {"constant_memory": True})
lx.write_excel_logs(args.logfiles, wb)
wb.close()
