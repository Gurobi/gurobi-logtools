# CHANGELOG
## Unreleased
### Added
### Fixed
### Changed
### Removed

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
