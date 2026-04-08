# Changelog

## [1.1.1] - 2026-04-07

### 🔒 Security Fixes
- Removed unicode control characters from SKILL.md and README.md
- Fixed placeholder URLs (yourusername → defzky)
- Added SECURITY.md with comprehensive security documentation
- Added network usage justification in manifest.json
- Fixed repository URL consistency

### 📝 Documentation
- Added SECURITY.md file
- Updated manifest.json with security notes
- Cleaned all markdown files

### 🐛 Bug Fixes
- Removed .git folder from package
- Removed __pycache__ directories
- Removed binary .pyc files

---

## [1.1.0] - 2026-04-07
 - 2026-04-07

### ✨ New Features
- **Contraction Timer** - Track labor contractions with timing and intensity
  - `/contraction start` - Start timing contraction
  - `/contraction end [intensity]` - End with mild/moderate/strong
  - `/contraction summary` - View all contractions
  - `/contraction hospital` - When to go to hospital guide
  
- **Kick Counter** - Track baby movements
  - `/kick log` - Log a single kick
  - `/kick start` - Start kick counting session (count to 10)
  - `/kick add [type]` - Add kick/roll/hiccup
  - `/kick summary` - View kick history
  - `/kick guide` - Kick counting guide

### 📝 Documentation
- Updated README with new features
- Updated command list

### 🐛 Bug Fixes
- Removed binary files from package
- Fixed import issues

---

## [1.0.0] - 2026-04-07

### ✨ Initial Release
- Indonesian foods guide
- Traditional recipes
- Morning sickness tips
- Young mom nutrition
- Hospital bag checklist
- BPJS coverage guide
- Financial planning tools
- Pregnancy tracking
