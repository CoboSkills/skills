---
name: shipping-cost-calculator-ecommerce
description: Estimate ecommerce shipping cost per order across weight, zones, carrier rules, and free-shipping policies so teams can make better pricing, margin, and offer-design decisions.
---

# Shipping Cost Calculator Ecommerce

Estimate shipping as a margin and offer-design decision, not just a carrier quote lookup.

## Use when

- You need to understand how shipping affects unit economics
- A team is testing free shipping, threshold-based shipping, bundles, or pricing changes
- You want to compare zones, carriers, or packaging assumptions
- Certain regions or order profiles may be quietly unprofitable

## Do not use when

- You need live carrier API rates with guaranteed contractual accuracy
- Packaging, zones, or weight assumptions are completely unknown
- The task is warehouse operations design beyond shipping-cost estimation
- You only need a public quote screenshot with no business interpretation

## Inputs

- origin and destination regions / zones
- package weight, dimensions, and volumetric rules if relevant
- carrier or 3PL pricing inputs
- pick-pack, fulfillment, packaging, label, and handling costs
- free-shipping rules or threshold policy
- average order value / bundle assumptions if relevant
- optional loss assumptions: reshipments, return shipping, damaged parcels

## Workflow

1. Estimate true per-order shipping cost, including fulfillment-adjacent costs.
2. Compare cost patterns by zone, weight band, or order profile.
3. Measure the margin impact of free shipping or threshold offers.
4. Identify where shipping economics break down.
5. Recommend decision levers: threshold change, packaging change, carrier change, pricing adjustment, or regional restriction.

## Output

1. Assumptions table
2. Shipping cost estimate by order or segment
3. Margin / pricing impact view
4. Policy impact view for free shipping or thresholds
5. Recommended actions and risk notes

## Quality bar

- Should reflect true fulfillment cost, not just carrier line-item price
- Should make high-risk regions or order types easy to spot
- Should be useful for pricing and promo design decisions
- Should avoid fake precision when assumptions are rough

## What better looks like

Better output does not stop at “shipping costs $X.”
It helps answer:
- can we afford free shipping?
- what threshold actually works?
- which region is killing margin?
- should we bundle, reprice, or change packaging?
- where are we underestimating total delivery cost?

## Resource

See `references/output-template.md`.
