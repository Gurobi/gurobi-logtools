# CHANGELOG
## Unreleased
- rename project to gurobi-logtools for consistency with other Gurobi projects

### Added
- add Python 3.11 tests

### Fixed
### Changed
### Removed

## 2.2.0 - 2023-08-25
### Added
- Command line option to copy/rename log files according to parameter settings (#34)

## 2.1.0 - 2023-04-27
### Added
- Parsing of deterministic work metric in nodelog, barrier, and simplex (#27)
- Add a ChangedParams summary column with parameters as a dictionary (#21)
### Fixed
- Handle pandas warning related to groupby(); fix join issue in pandas2 (#29,#33)

## 2.0.0 - 2022-04-04
### Changed
- The code went through a refactoring while it remains backward compatible.
- Seed and Time columns in the DataFrame are reported as integer and datetime types, respectively
- The `get_dataframe(logfiles, timelines=False, prettyparams=False)` API has a new signature
- A new API `parse(patterns)` is added that returns a `ParseResult()` object with `summary()` and `progress(section)` methods (see README.md for an example usage)


## 1.3.2 - 2022-01-12
### Fixed
- fix error when log contains cuts with the name containing a hyphen

## 1.3.1 - 2021-Dec-14
### Fixed
- fix error when log does not have a tree section

## 1.3.0 - 2021-Dec-03
### Changed
- refactor to make code more modular
### Fixed
- avoid coercing NewSolution to numeric type

## 1.2.2 - 2021-Nov-23
### Added
- update default parameter list for v9.5.0

## 1.2.1 - 2021-Nov-18
### Added
- add counter to LogFilePath to better distinguish merged logs

## 1.2.0 - 2021-Nov-09
### Added
- new parameter `prettynames=True` to replace parameter values with meaningful descriptions
### Fixed
- fix parsing of MIP Start information

## 1.1.0 - 2021-Oct-26
### Added
- add missing range attributes for quadratic constraints

## 1.0.0 - 2021-Oct-06
### Added
- parse output from NoRel heuristic into separate DataFrame (included in `timelines` dictionary)
### Changed
- new output format for timelines:
  - second return value (when using option `timelines=True`) is now a dictionary including the individual timeline DataFrames, that is `rootlp`, `nodelog`, and `norel`
  - see README for updated usage information

## 0.3.2 - 2021-Aug-25
### Added
- support Compute Server log files
- add Cores count

## 0.3.1 - 2021-Aug-23
- initial public release
