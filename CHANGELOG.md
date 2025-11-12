# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2025-11-11

### Added
- Initial release with Kokoro TTS support
- Asynchronous speech generation
- Automatic audio resampling and normalization
- Comprehensive test suite
- Example applications in `main.py`
- CI/CD pipeline with GitHub Actions

### Changed
- Migrated from ElevenLabs to Kokoro for TTS generation
- Improved error handling and logging

### Deprecated
- ElevenLabs integration (kept for backward compatibility)

---

## Versioning

- **Major** (X.0.0): Breaking Changes, neue Architektur
- **Minor** (0.X.0): Neue Features, abwärtskompatibel
- **Patch** (0.0.X): Bugfixes, kleine Verbesserungen
