# The following runs on linux or MacOS and requires pyenv to be installed.
#  Additionally the relevant Python runtimes should be installed.
#  It should be run from the project root directory.

pyenv local 3.6

for s in 9.1.0 9.1.1 9.1.2; do
    python -m venv .paramdefs
    ./.paramdefs/bin/python -m pip install --upgrade pip
    ./.paramdefs/bin/python -m pip install gurobipy==$s
    ./.paramdefs/bin/python scripts/generate-defaults.py;
    rm -rf .paramdefs
done

pyenv local 3.10

for s in 9.5.0 9.5.1 9.5.2 10.0.0 10.0.1 10.0.2 10.0.3 11.0.0 11.0.1 11.0.2; do
    python -m venv .paramdefs
    ./.paramdefs/bin/python -m pip install --upgrade pip
    ./.paramdefs/bin/python -m pip install gurobipy==$s
    ./.paramdefs/bin/python scripts/generate-defaults.py;
    rm -rf .paramdefs
done
