---
name: insurance
description: Personal and business insurance management with policy tracking and claims support. Use when user mentions insurance policies, coverage review, filing claims, comparing policies, or understanding coverage gaps. Tracks all policies, documents, renewal dates, and helps prepare for claims. NEVER provides insurance advice or recommends specific coverage amounts.
---

# Insurance

Insurance organization system. Know what you have, find what you need.

## Critical Privacy & Safety

### Data Storage (CRITICAL)
- **All insurance data stored locally only**: `memory/insurance/`
- **No external APIs** for insurance data
- **No connection** to insurance company systems
- **No policy purchases** through this skill
- User controls all data retention and deletion

### Safety Boundaries (NON-NEGOTIABLE)
- ✅ Track policy details and coverage
- ✅ Log claims and documentation
- ✅ Compare policy features side-by-side
- ✅ Flag renewal dates and coverage gaps
- ❌ **NEVER provide insurance advice** on coverage needs
- ❌ **NEVER recommend specific coverage amounts**
- ❌ **NEVER replace** licensed insurance agents
- ❌ **NEVER facilitate policy purchases**

### Legal Disclaimer
Insurance decisions depend on individual circumstances, jurisdiction, and specific policy terms. This skill helps you understand your coverage and identify gaps. Always work with a licensed insurance agent or broker for significant coverage decisions.

## Quick Start

### Data Storage Setup
Insurance records stored in your local workspace:
- `memory/insurance/policies.json` - All policy details
- `memory/insurance/claims.json` - Claims history and status
- `memory/insurance/documents.json` - Policy documents inventory
- `memory/insurance/renewals.json` - Renewal tracking
- `memory/insurance/coverage_gaps.json` - Identified gaps

Use provided scripts in `scripts/` for all data operations.

## Core Workflows

### Add Policy
```
User: "Add my home insurance policy"
→ Use scripts/add_policy.py --type home --carrier "State Farm" --premium 1200
→ Log policy details, coverage limits, deductibles
```

### Log Claim
```
User: "I need to file an auto insurance claim"
→ Use scripts/log_claim.py --policy auto --incident "accident" --date 2024-03-01
→ Document incident, track claim status, prepare required info
```

### Review Coverage
```
User: "Review my insurance coverage"
→ Use scripts/review_coverage.py
→ Show all policies, identify gaps, flag upcoming renewals
```

### Compare Policies
```
User: "Compare these two health insurance plans"
→ Use scripts/compare_policies.py --policy1 planA --policy2 planB
→ Side-by-side comparison of coverage, costs, networks
```

### Check Renewals
```
User: "Any insurance renewals coming up?"
→ Use scripts/check_renewals.py --days 60
→ Show policies renewing soon with premium changes
```

## Module Reference

For detailed implementation:
- **Policy Management**: See [references/policy-management.md](references/policy-management.md)
- **Health Insurance**: See [references/health-insurance.md](references/health-insurance.md)
- **Home/Renters Insurance**: See [references/home-insurance.md](references/home-insurance.md)
- **Auto Insurance**: See [references/auto-insurance.md](references/auto-insurance.md)
- **Life Insurance**: See [references/life-insurance.md](references/life-insurance.md)
- **Claims Process**: See [references/claims.md](references/claims.md)
- **Renewal Review**: See [references/renewals.md](references/renewals.md)

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `add_policy.py` | Add new insurance policy |
| `log_claim.py` | Log and track insurance claim |
| `review_coverage.py` | Review all coverage and gaps |
| `compare_policies.py` | Compare two policies side-by-side |
| `check_renewals.py` | Check upcoming renewals |
| `add_document.py` | Log policy document |
| `identify_gaps.py` | Identify potential coverage gaps |
| `generate_summary.py` | Create insurance portfolio summary |

## Disclaimer

This skill helps you understand and organize your insurance coverage. For coverage decisions and complex situations, always work with a licensed insurance agent or broker.
