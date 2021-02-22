# Changelog

## [Unreleased]
### Changed
- Recognize TIF and WEBP image extensions
- Look for image URLs in <media:thumbnail />
- Updated requirements.txt package versions

## [1.0.6] - 2020-11-01
### Fixed
- Updated feedparser requirement for python 3.9 compatibility

## [1.0.5] - 2020-08-01
### Changed
- Updated requirements.txt package versions

## [1.0.4] - 2020-01-31
### Changed
- Updated requirements.txt package versions
### Fixed
- Handle missing fields more gracefully

## [1.0.3] - 2019-12-03
### Changed
- Updated requirements.txt package versions

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
[1.0.3]: https://gitlab.com/brianodonnell/pod_feeder_v2/compare/1.0.2...1.0.3
[1.0.4]: https://gitlab.com/brianodonnell/pod_feeder_v2/compare/1.0.3...1.0.4
[1.0.5]: https://gitlab.com/brianodonnell/pod_feeder_v2/compare/1.0.4...1.0.5
[1.0.6]: https://gitlab.com/brianodonnell/pod_feeder_v2/compare/1.0.5...1.0.6
