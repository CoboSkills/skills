---
name: designers-eye
description: "Professional design critique tool that visually analyzes designs (screenshots, live URLs, social posts, websites, web apps, mockups) and provides priority-ordered improvement suggestions. Uses Gestalt principles, visual hierarchy, colour theory (WCAG), typography, UX heuristics (Nielsen's 10), and platform conventions (web/mobile/social/email). Generates actionable critique ranked by severity—critical fixes first, then important improvements, then polish. Use for (1) getting design feedback on mockups/screenshots, (2) auditing live websites or web apps, (3) critiquing social media posts, (4) reviewing Figma exports and design exports, (5) learning design principles through real examples. Triggers on phrases like critique this design, review my mockup, what's wrong with this design, design feedback, design critique, or when an image/URL is shared with design or critique mentioned."
---

# Designers Eye — Professional Design Critique

A critical eye for design. Share a screenshot, image, or website URL and get honest, theory-backed feedback prioritized by impact.

## How It Works

**Input:** Screenshot, image file (PNG/JPG/GIF), PDF export, or live URL.

**Analysis:** Examined through six lenses—Gestalt principles, visual hierarchy, colour/contrast, typography, UX heuristics, and platform conventions.

**Output:** Priority-ordered action list (critical → important → polish) with specific fixes and principles violated.

## Input Formats

### Screenshots or Images
Share or upload directly in chat. Works for web apps, websites, mockups, social posts, any visual design.

### Figma Designs
Export a frame or screen from Figma as a PNG/JPG and share that. Screenshot-based analysis works well — no API integration required.

### Live URLs
Share a public website URL. The agent will fetch and analyse the page visually.

**Localhost URLs** (`http://localhost:xxxx`) — only work if the agent has direct access to your local machine. If it doesn't, take a screenshot instead.

### PDF Designs
PDFs aren't analysed directly. Export the relevant pages as PNG/JPG images and share those — works just as well for layout and design critique.

### Social Media Posts
Share a screenshot of a social post (Instagram, Twitter/X, LinkedIn, TikTok) or the post content itself.

---

## Analysis Framework

Every critique is structured through these six lenses:

**1. Gestalt Principles** — How elements group and relate (proximity, similarity, continuity, closure, figure/ground, common fate, prägnanz, uniform connectedness). See `references/gestalt.md`.

**2. Visual Hierarchy** — What's the focal point? Are reading paths clear? Do size, weight, colour, position, and whitespace align? See `references/visual-hierarchy.md`.

**3. Colour Theory & Accessibility** — Do colours work together? Does contrast meet WCAG AA (4.5:1 for text, 3:1 for UI)? Is the design colourblind-friendly? See `references/colour-theory.md`.

**4. Typography** — Is the type scale coherent? Do font pairings make sense? Are sizes readable (16px+ for body)? Line length optimal (45–75 chars)? Line height breathable (1.5+)? See `references/typography.md`.

**5. UX/Usability Heuristics** — Does the design follow Nielsen's 10 usability heuristics? Can users recover from errors? Is it clear what's interactive? See `references/ux-heuristics.md`.

**6. Platform Conventions** — Does it follow web, mobile, social, or email norms? Are safe zones respected? Is it thumb-friendly on mobile? See `references/platform-conventions.md`.

---

## Output Format — Priority-Ordered Action List

Findings are grouped by severity. Fix critical issues first.

### 🔴 Critical
Issues that break usability, accessibility, or core functionality. Fix immediately.

Example:
```
🔴 Critical — Text contrast fails WCAG AA
The white text on your light blue background achieves 3.2:1 contrast (need 4.5:1 for AA).
This violates: Accessibility / WCAG contrast requirement
Fix: Darken the blue to #0052CC or lighten the text to #F5F5F5. Verify contrast with a checker.
```

### 🟡 Important
Issues that hurt the experience or violate design principles without breaking core function. Fix soon.

Example:
```
🟡 Important — Hierarchy collapse in the heading area
Your H1 (28px) and H2 (24px) sizes violate the type scale ratio (need ~1.25× gap = 35px vs 28px).
This violates: Visual hierarchy / Type scale consistency
Fix: Increase H1 to 35px or decrease H2 to 22px to create a clear scale.
```

### 🟢 Polish
Issues that elevate the design or address missed opportunities. Fix when time allows.

Example:
```
🟢 Polish — Spacing rhythm could be tightened
Your card padding is 20px but section margins are 40px, creating an inconsistent rhythm.
This violates: Gestalt proximity / Visual rhythm consistency
Fix: Use an 8px or 16px grid consistently. Stick to multiples: 8px, 16px, 24px, 32px, 40px, 48px.
```

---

## Workflow

1. **Share the design** — Screenshot, Figma URL, live URL, or image
2. **Specify if needed** — "Critique this" or "What can I improve?"
3. **Receive critique** — Prioritized list of findings with specific fixes

---

## What This Skill Does NOT Do

- **Doesn't redesign** — You get critique and fixes, not new mockups
- **Doesn't make subjective calls** — "Pink is better than blue" isn't critique; principle-based feedback is
- **Doesn't analyze branding alone** — Focuses on usability, hierarchy, and principles, not "does this feel on-brand?"
- **Doesn't inspect code** — Visual critique only

---

## Reading the References

This skill comes with six detailed reference files on the theory behind the critique. You don't need to read them all up front—they're there if you want to understand *why* something is a problem.

- **gestalt.md** — Gestalt principles with violations and fixes
- **visual-hierarchy.md** — Building and assessing visual hierarchy
- **colour-theory.md** — Colour relationships, harmony, WCAG contrast
- **typography.md** — Type scales, readability, font pairing
- **ux-heuristics.md** — Nielsen's 10 usability heuristics + affordance
- **platform-conventions.md** — Web, mobile, social, email, dark mode norms

---

## Tips for Getting Better Critiques

1. **Be specific about platform** — "This is a web app" vs. "This is a mobile app" changes the critique (touch targets, navigation patterns differ).
2. **Share context** — Is this a v1 rough draft or polished production? Critiques adjust.
3. **Ask a specific question if helpful** — "Does the CTA stand out?" or "Is the hierarchy clear?" focuses the analysis.
4. **Don't defend your choices** — Critique is feedback, not attack. It's about improving the design, not your ego.
5. **Test fixes** — Once you implement, share again if you want confirmation that it's better.

---

## Examples of Good Critiques to Request

- "Critique this landing page screenshot"
- "What should I fix in this design? [share Figma export or screenshot]"
- "Design review: https://example.com — any glaring issues?"
- "Is this social post readable at thumbnail size?" (share screenshot)
- "Visual feedback on this app mockup — focusing on hierarchy" (share image)

---

## Example Critique (Real Output)

```
Design: Social Media Post (Instagram)

🔴 Critical — Text unreadable at thumbnail size
Your white body text on the light grey background is 12px and achieves ~2.8:1 contrast. 
At Instagram feed thumbnail (1/4 size), this text becomes invisible.
This violates: Platform conventions (social post safe zone) / Contrast (WCAG AA)
Fix: Use 24px minimum for text on social posts. Increase contrast to 4.5:1. Consider adding a 
dark scrim behind the text (0 0 0 / 40%) to guarantee readability.

🟡 Important — CTA buried in caption
Your "Learn more" link is at the bottom of the post, but Instagram feed shows ~2 lines of caption 
before cut-off. Most users won't see it.
This violates: Platform conventions (Instagram CTA placement)
Fix: Move the CTA to the post caption's first line, or add a visual CTA element (button, arrow, shape) 
to the image itself pointing to the link.

🟡 Important — Colour harmony feels chaotic
You're using a bright magenta (#FF00FF), teal (#00FFFF), and orange (#FF8800) at full saturation. 
The eye has no clear focal colour.
This violates: Visual hierarchy (one focal colour per view) / Colour harmony
Fix: Keep magenta as the primary, desaturate the teal to 40%, and use orange sparingly as an accent 
on the CTA only. Test on both light and dark mode.

🟢 Polish — Heading typeface choice feels inconsistent
Your display font (Playfair Display) pairs well with the body (Open Sans), but the geometric weight 
of Playfair feels at odds with the organic nature of the imagery.
This violates: Typography (font pairing harmony)
Fix: Test a humanist serif (Georgia, IM Fell English) or a warm sans (Raleway) as an alternative. 
The goal is visual cohesion between typeface and subject matter.
```

---

## Notes

- Critiques are honest and principle-based, not personal
- Fixes are specific and actionable — not vague suggestions
- Priority levels help you focus: fix critical first, important second, polish when time allows
- Every finding cites which design principle(s) it violates
