import argparse
import xlsxwriter
import grblogtools as glt

parser = argparse.ArgumentParser(description="grblogtools "+glt.__version__, prog="grblogtools")
parser.add_argument("outfile", help="Output file name (.xlsx)", metavar="XLSXFILE")
parser.add_argument(
    "logfiles", help="Gurobi log files", nargs="+", metavar="LOGFILE"
)
args = parser.parse_args()

wb = xlsxwriter.Workbook(args.outfile, {"constant_memory": True})
glt.write_excel_logs(args.logfiles, wb)
wb.close()
