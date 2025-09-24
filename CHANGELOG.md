# CHANGELOG
## Unreleased
### Fixed
- PresolvedNumConVars, PresolvedNumIntVars and PresolvedNumBinVars data is populated from presolved model stats (#GH89)

### Changed
### Removed
### Added
- Added support for parsing finer details in multi-objective logs (#GH36)
- Added the `warnings_action` parameter to `gurobi_logtools.parse` (#GH88)
- NumConVars, NumIntVars and NumBinVars are added to capture variable types in original model (#GH89)
- Added parsing for parameters under "Non-default parameters" section in logs (#GH92)

## 4.0.1 - 2025-08-14
### Fixed
- fixed deprecation warning for button style (#GH83)

## 4.0.0 - 2025-07-25
### Fixed
- fixed platform-specific issues in tests with file and path handling
### Changed
- New defaults for dashboard widgets
- Updated data folder and gurobi-logtools.ipynb notebook
### Removed
- remove Python 3.8 support
### Added
- All parsers now additionally return the result of a parsed line. This enables live usage within a Gurobi Callback.
- Added "Parameters" column when plotting summary DataFrame to facilitate aesthetic parameter labels
- Added ECDF to plot types
- Added widget to dashboard fields for "points" and "barmode"
- Added widgets to dashboard related to palettes
- Added button to dashboard to swap x and y axes
- Added widgets to dashboard for title, x-axis label, y-axis label
- Added widgets to dashboard for height and width
- Added toggles to dashboard for boxplot means, boxplot notches, reversing ecdf and legend visibility
- Added widgets to facilitate sorting either x or y axis by a particular data column and aggregation metric
- Added buttons to save and load widget config (i.e. values)
- Added a query field to dashboard to enable filtering of data "on the fly""
- Added an "parameters to ignore" field to dashboard to give finer control over "Parameters" column
- Added new top level functions: `gurobi_logtools.register_custom_palette`, `gurobi_logtools.reset_custom_palettes`, `gurobi_logtools.show_palettes`, `gurobi_logtools.get_plotly_fig`, `gurobi_logtools.save_plot`
- Added `--progress` to alias the `--timelines` option in the command line interface

## 3.2.0 - 2024-12-19
### Fixed
- Logs ending with memory or work limit reached, will now return a corresponding status
### Changed
- If logfiles are not found when parsing then a FileNotFoundError is raised

## 3.1.0 - 2024-07-25
### Changed
- Parsing of heuristic solutions found prior to nodelog (but not found by NoRel) (#51)
- slightly reorganized parsers
- better parsing of early solutions (pre-tree and norel)

## 3.0.0 - 2023-10-11
### Changed
- rename project to gurobi-logtools for consistency with other Gurobi projects
### Added
- add Python 3.11 tests

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
