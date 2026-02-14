# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-02-14

### Added
- Makefile for easy setup, installation, linting, testing, and pre-commit tasks.
- Automatic linting with ruff in GitHub Actions workflows.
- Separate workflows for publishing to PyPI and TestPyPI.
- Import test for TimerSentinel and shortcut import in `__init__.py`.
- First develop release published to TestPyPI.
- Added ruff linter command to use `ruff check` in CICD.

### Changed
- Improved tag patterns in workflows to better distinguish releases and pre-releases.
- Updated logging setup in TimerSentinel for clarity and consistency.

### Fixed
- Removed trailing newlines in configuration and test files for consistency.
- Added conditional checks for release-build and pypi-publish jobs for more robust CI.

## [0.1.0] - 2026-02-13

### Added
- Initial release
- Support for context manager usage
- Support for decorator usage (sync and async)
- Manual timer control (start/end/report)
- Configurable logging with custom levels and keywords
- Optional callbacks on threshold exceed with arguments
- Automatic function name detection when used as decorator
- Full type hints for better IDE support
- Optimized with `__slots__` for performance
- 100% test coverage
- Support for Python 3.10+

### Features
- High precision timing using `time.perf_counter()`
- Unique execution IDs for each timer instance
- Flexible configuration options
- Works with both synchronous and asynchronous functions
- Clean exception propagation
- Comprehensive documentation
