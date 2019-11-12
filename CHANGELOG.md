# Changelog

## [Unreleased]

## [1.0.2] - 2019-11-12
### Added
- Add unit tests
### Changed
- Refactor parts of `pod_feeder.py` to make unit testing easier
- Updated requirements.txt package versions

## [1.0.1] - 2019-07-02
### Fixed
- Change package dependency from `diaspy` to `diaspy-api`

## [1.0.0] - 2019-07-02
### Added
- First official release
- Add `pod-feeder` and `pf-clean-db` console scripts

### Changed
- Convert to an install-able package

### Deprecated
- Symlinks to `pod_feeder.py` and `clean_db.py` were created for legacy users who
  installed directly from source. These will be removed in a future release in favor of
  the `pod-feeder` and `pf-clean-db` console scripts.

[Unreleased]: https://gitlab.com/brianodonnell/pod_feeder_v2/compare/1.0.2...master
[1.0.0]: https://gitlab.com/brianodonnell/pod_feeder_v2/-/tags/1.0.0
[1.0.1]: https://gitlab.com/brianodonnell/pod_feeder_v2/compare/1.0.0...1.0.1
[1.0.2]: https://gitlab.com/brianodonnell/pod_feeder_v2/compare/1.0.1...1.0.2
