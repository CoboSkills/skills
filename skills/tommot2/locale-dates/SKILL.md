---
name: locale-dates
description: "Format dates and times for any locale. 100+ country patterns, timezone conversion, relative time, duration calculation, weekday/month names in local language. Covers ISO 8601, European, American, Japanese, Chinese, Arabic, and more. Use when: (1) format a date or time, (2) convert timezone, (3) 'what time is it in Tokyo', (4) 'how many days until X', (5) locale-specific formatting, (6) ISO 8601 timestamps, (7) heartbeat/cron time display, (8) relative time like '3 hours ago' or 'in 2 days', (9) date format conventions by country. Eliminates date confusion across international teams and multi-timezone workflows. No external dependencies. Homepage: https://clawhub.ai/skills/locale-dates"
---

# Date/Time Formatting

**Install:** `clawhub install locale-dates`

Provide dates and times in the user's preferred format. Detect format from the user's message or ask if unclear.

## Quick Reference

See [references/locales.md](references/locales.md) for the full locale lookup table (100+ entries).

## Decision Flow

1. **Check preference** - Ask the user if they have a preferred format.
2. **Ask if unclear** - If no preference is saved and context doesn't imply one, ask: *"Hvilket datoformat foretrekker du? (ISO 8601, norsk DD.MM.YYYY, amerikansk MM/DD/YYYY, etc.)"*
3. **Remember** - Use the selected format for this session.

## Format Components

### Date Formats

| Format | Pattern | Example | Used By |
|--------|---------|---------|---------|
| ISO 8601 (full) | `YYYY-MM-DD` | `2026-03-27` | International standard |
| ISO 8601 datetime | `YYYY-MM-DDTHH:mm:ss±HH:MM` | `2026-03-27T18:30:00+01:00` | Technical, logs, APIs |
| ISO 8601 basic | `YYYYMMDDTHHmmssZ` | `20260327T173000Z` | Compact technical use |
| European | `DD.MM.YYYY` | `27.03.2026` | Norway, Germany, most of EU |
| European long | `DD. MMMM YYYY` | `27. mars 2026` | Norwegian text |
| American | `MM/DD/YYYY` | `03/27/2026` | United States |
| UK | `DD/MM/YYYY` | `27/03/2026` | United Kingdom, Ireland, Australia |
| Japanese | `YYYY年MM月DD日` | `2026年03月27日` | Japan |
| Chinese | `YYYY年M月D日` | `2026年3月27日` | China |
| Korean | `YYYY년 MM월 DD일` | `2026년 03月 27일` | South Korea |
| Indian | `DD-MM-YYYY` | `27-03-2026` | India |
| Thai (Buddhist) | `DD/MM/BYYYY` | `27/03/2569` | Thailand |

### Time Formats

| Format | Pattern | Example | Used By |
|--------|---------|---------|---------|
| 24-hour | `HH:mm` | `18:30` | Most of the world |
| 24-hour with seconds | `HH:mm:ss` | `18:30:00` | Technical, logs |
| 12-hour | `h:mm AM/PM` | `6:30 PM` | United States, Philippines |
| 12-hour with seconds | `h:mm:ss AM/PM` | `6:30:00 PM` | United States |
| Japanese | `HH時mm分` | `18時30分` | Japan |

### Combined Datetime Formats

| Format | Pattern | Example |
|--------|---------|---------|
| ISO 8601 (recommended) | `YYYY-MM-DDTHH:mm:ss±HH:MM` | `2026-03-27T18:30:00+01:00` |
| ISO 8601 (UTC) | `YYYY-MM-DDTHH:mm:ssZ` | `2026-03-27T17:30:00Z` |
| Norwegian | `DD.MM.YYYY kl. HH:mm` | `27.03.2026 kl. 18:30` |
| American | `MM/DD/YYYY, h:mm AM/PM` | `03/27/2026, 6:30 PM` |
| British | `DD/MM/YYYY, HH:mm` | `27/03/2026, 18:30` |
| Japanese | `YYYY年MM月DD日 HH時mm分` | `2026年03月27日 18時30分` |

### Relative Time & Duration

When users ask about time differences or relative dates:

| Query Type | Example | Response Format |
|-----------|---------|----------------|
| Time ago | "3 hours ago" | `2026-03-29 kl. 05:00` (calculated from now) |
| Time until | "in 2 days" | `2026-03-31 kl. 09:04` (calculated from now) |
| Duration between | "how many days between X and Y" | `47 days` or `6 weeks and 5 days` |
| Next occurrence | "next Friday" | `2026-04-03` with locale format |
| Timezone convert | "what time is it in Tokyo" | `17:04 JST (2026-03-29T17:04:00+09:00)` |

### Timezone Conversion

When converting between timezones, always show:
1. Target time in target timezone
2. Target time in user's timezone (for reference)
3. UTC equivalent

```
Tokyo: 17:04 JST
Oslo: 09:04 CET (same moment)
UTC:  08:04
```

## Heartbeat / Cron Timestamps

When displaying timestamps in heartbeat or cron messages, always include:

- **Current time**: The actual time when the message is generated
- **Trigger time** (if different): When the event was scheduled to fire

Use ISO 8601 as the default for machine-readable timestamps, with the user's locale format alongside for readability:

```
Current time: 2026-03-27T18:30:00+01:00 (27.03.2026 kl. 18:30)
Heartbeat triggered at: 2026-03-27T04:00:00+01:00
```

## Locale Lookup

For country-specific formats, consult [references/locales.md](references/locales.md). Each entry includes:
- Date format
- Time format
- Time separator
- First day of week
- 12h/24h preference

## Saving Preferences

When a user specifies a format preference, remember it for this session:

```markdown
## Preferences

- **Date format**: ISO 8601 (YYYY-MM-DD)
- **Time format**: 24-hour (HH:mm)
- **Datetime format**: YYYY-MM-DDTHH:mm:ss±HH:MM
- **Locale**: Europe/Oslo
```
