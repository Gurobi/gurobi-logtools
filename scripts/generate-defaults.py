"""
Kept in scripts as we do not want gurobi-logtools to depend on gurobipy (since it
would then require a license/consume a token/open a compute server session in
order to look up basic parameter information). This script can instead be used
to generate a default parameters file gurobi-logtools can read from.

If all past gurobi versions and a python3.6 binary are all available,
generate all defaults files using :

    for s in 800 801 810 811 900 901 902 903 910 911 912; do
        LD_LIBRARY_PATH=/opt/gurobi$s/linux64/lib \
        PYTHONPATH=/opt/gurobi$s/linux64/lib/python3.6_utf32 \
        python3.6 scripts/generate-defaults.py;
    done

There aren't usually default parameter changes in technical releases (?) but it
seems easiest just to store one file for each version.
"""

import json
import os
import pathlib

import gurobipy as gp

# Find parameter defaults using model.Params and model.getParamInfo
# Note: getParamInfo() gives values in the following order:
#     ["name", "type", "current", "min", "max", "default"]
model = gp.Model()
default_parameter_values = {
    parameter: default
    for parameter, default in (
        (attr, model.getParamInfo(attr)[-1])
        for attr in dir(model.Params)
        if not (attr.startswith("_") or attr.endswith("_"))
    )
    if type(default) is not str
    and not parameter.startswith("CS")
    and not parameter.startswith("Tune")
}

# Store parameter defaults in a file tagged with the release version.
defaults_dir = pathlib.Path(__file__).parent.parent.joinpath(
    "src/gurobi_logtools/parameters/data"
)
target_file = defaults_dir.joinpath(
    f"{gp.GRB.VERSION_MAJOR}{gp.GRB.VERSION_MINOR}{gp.GRB.VERSION_TECHNICAL}.json"
)
print(target_file)
os.makedirs(defaults_dir, exist_ok=True)
with target_file.open("w") as outfile:
    json.dump(default_parameter_values, outfile, indent=4, sort_keys=True)
