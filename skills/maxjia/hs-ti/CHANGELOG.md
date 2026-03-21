# Changelog

All notable changes to hs-ti will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.9] - 2026-03-21

### Fixed
- **Example File Imports**: Fixed import statements in example files
  - Updated `query_ioc.py` to import `hs_ti_plugin` instead of `yunzhan_plugin`
  - Updated `batch_query_ips.py` to import `hs_ti_plugin` instead of `yunzhan_plugin`
- **Package Metadata**: Corrected config declaration in package.json
  - Moved config declaration to root level for proper registry metadata
  - Changed file reference from `config.example.json` to `config.json`
  - Removed duplicate config declaration in openclaw section
  - Added description field for better documentation

## [1.1.8] - 2026-03-21

### Fixed
- **Documentation Consistency**: Updated SKILL.md to clarify config.json creation process
  - Added step-by-step instructions for copying config.example.json to config.json
  - Improved bilingual documentation for configuration setup
- **Test File Naming**: Renamed test_yunzhan.py to test_hs_ti.py for consistency
- **Package Test Script**: Updated package.json test script to use new test file name

## [1.1.7] - 2026-03-21

### Changed
- **Plugin File Renamed**: Renamed `yunzhan_plugin.py` to `hs_ti_plugin.py` for consistency with skill name
- **Package Entry Point**: Updated package.json main field to `scripts/hs_ti_plugin.py`

### Removed
- **config.json**: Removed config.json from published package
- **Template Only**: Now only config.example.json is included as a template for users

## [1.1.6] - 2026-03-20

### Added
- **Advanced API Support**: Added support for advanced threat intelligence API endpoints
  - New `-a` parameter to call advanced API (e.g., `/threat-check -a 45.74.17.165`)
  - Advanced API provides detailed information including:
    - Basic info: network, carrier, location, country, province, city, coordinates
    - ASN information
    - Threat type and tags
    - DNS records (up to 10)
    - Current and historical domains (up to 10)
    - File associations: downloaded, referenced, and related file hashes (malicious only)
    - Port information: open ports, protocols, application names, versions
  - Updated documentation with advanced API usage examples and endpoint details

## [1.1.5] - 2026-03-20

### Added
- **Better Error Messages**: Enhanced API key configuration error messages
  - Added detailed configuration instructions in both Chinese and English
  - Users now receive clear guidance on how to configure their API key when it's missing or set to default value
  - Error messages include file path and step-by-step instructions

## [1.1.4] - 2026-03-20

### Fixed
- **Security Compliance**: Fixed config file inclusion issue
  - Removed config.json from .npmignore to ensure it's included in published package
  - Added config.example.json as template for users
  - Updated package.json to reference config.example.json
  - Updated README.md with instructions for copying config.example.json to config.json
- **API URL**: Corrected API URL from https://ti.hillstonenet.com.cn to https://ti.hillstonenet.com.cn (removed extra 's')

## [1.1.3] - 2026-03-20

### Added
- **Display Title**: Added title field to SKILL.md metadata for better display on clawhub.ai as "Hillstone Threat Intelligence"

## [1.1.2] - 2026-03-20

### Added
- **Display Name**: Added displayName field to package.json for better display on clawhub.ai as "Hillstone Threat Intelligence"

## [1.1.1] - 2026-03-20

### Fixed
- **Skill Description**: Updated SKILL.md frontmatter description to include both Chinese and English for better display on clawhub.ai

## [1.1.0] - 2026-03-20

### Added
- **Bilingual Support (CN/EN)**: Added full Chinese/English bilingual support
  - Default language: English
  - Command `/hs-ti cn` to switch to Chinese
  - Command `/hs-ti en` to switch to English
  - All user-visible content now supports language switching
- **CHANGELOG.md**: Added comprehensive changelog to track all version changes
- **Language Configuration**: Added language preference storage and switching logic
- **Enhanced Documentation**: Updated SKILL.md and README.md with bilingual content

### Changed
- **Package Metadata**: Updated package.json with language configuration support
- **Plugin Logic**: Modified yunzhan_plugin.py to support dynamic language switching

### Fixed
- **Security Compliance**: Added config and network declarations to package.json for security compliance (v1.0.1)

## [1.0.1] - 2026-03-20

### Fixed
- **Security Compliance**: Added config and network declarations to package.json
  - Declared config.json as required configuration file
  - Added schema for api_key and api_url
  - Declared network endpoints for transparency
  - Resolved security warnings from clawhub

## [1.0.0] - 2026-03-20

### Added
- **Initial Release**: First release of hs-ti (Hillstone Threat Intelligence)
- **IOC Query Support**: Support for IP, Domain, URL, and File Hash queries
- **Batch Query**: Support for querying multiple IOCs at once
- **Performance Statistics**: Real-time response time tracking
- **Cumulative Monitoring**: Historical performance metrics
- **Detailed Threat Info**: Returns threat type, credibility, and classification

### Features
- IP reputation query
- Domain reputation query
- URL reputation query
- File hash reputation query (MD5/SHA1/SHA256)
- Batch query support (comma-separated IOCs)
- Real-time response time statistics
- Cumulative performance monitoring

### Documentation
- Comprehensive README.md with installation and usage instructions
- SKILL.md with OpenClaw integration details
- Example scripts for common use cases
- Test suite for validation