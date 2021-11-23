# CHANGELOG
## Unreleased
### Added
### Fixed
### Changed
### Removed

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
