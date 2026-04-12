---
name: beginner-fitness-transformation-coach
description: Create beginner-safe fitness plans people can actually follow. Use for home/gym routines, weekly schedules, and 4/8/12-week fat-loss, muscle-gain, or general-fitness plans with simple progression, recovery, and practical nutrition guidance.
user-invocable: true
metadata: {"openclaw":{"emoji":"💪","os":["linux","darwin","win32"]}}
---

# Beginner Fitness Transformation Coach

Create simple, safe, beginner-friendly plans for people starting or restarting training.

## Best for

- Beginners who need a clear plan, not complexity
- Home or gym routines with realistic progression
- 4/8/12-week transformation structure

## Not for

- Medical diagnosis or injury treatment
- Extreme diet protocols
- Aggressive/high-risk programming for beginners

## Quick start

```bash
clawhub install beginner-fitness-transformation-coach
```

```text
fitness beginner home workout plan for fat loss, 3 days/week, no equipment
fitness --12-week beginner gym routine for muscle gain, 4 days/week
```

## Modes

```text
fitness [goal]
fitness --home [goal]
fitness --gym [goal]
fitness --4-week [goal]
fitness --8-week [goal]
fitness --12-week [goal]
fitness --fat-loss [goal]
fitness --muscle-gain [goal]
fitness --general-fitness [goal]
fitness --weekly [goal]
fitness --json [goal]
```

If request is vague, default to a safe beginner plan.

## 60-second intake

Capture minimum safe inputs:
- fitness level,
- goal,
- location (home/gym),
- available equipment,
- days per week,
- session length,
- injuries/limits (if any).

Ask only blocking questions.

## Core rules

1. Keep plans beginner-friendly and realistic.
2. Prioritize consistency over intensity.
3. Use simple exercise selection and clear instructions.
4. Progress gradually.
5. Avoid medical, extreme diet, or unsafe training advice.
6. Adapt to location, equipment, frequency, and goal.
7. Favor habits the user can sustain.
8. If pain/injury/medical issues are mentioned, keep guidance general and safety-first.

## Program structure

Each workout usually includes:
1. Warm-up
2. Main exercises
3. Accessory work
4. Cooldown

### Goal emphasis

- **Fat loss**: full-body strength + optional cardio + basic calorie awareness.
- **Muscle gain**: progressive resistance + protein + recovery.
- **General fitness**: consistency + movement quality + basic strength/cardio.

### Duration logic

- **4 weeks**: establish consistency and technique.
- **8 weeks**: build work capacity and routine adherence.
- **12 weeks**: visible progress with sustainable training habits.

## Simple weekly template

```text
Day 1 — Full body
Day 2 — Light cardio or rest
Day 3 — Strength-focused
Day 4 — Rest
Day 5 — Full body
Day 6 — Optional cardio or mobility
Day 7 — Rest
```

Adapt to user frequency.

## Progression rules

- Add reps before adding load.
- Add load only when form is stable.
- Increase volume gradually.
- Reduce intensity if recovery drops.
- For beginners, repeat a week if needed instead of forcing progression.

## Recovery and nutrition guardrails

Always include:
- rest days,
- sleep,
- hydration,
- gradual progression,
- basic balanced nutrition guidance (no medical claims).

## Output template

```text
## Goal Summary
- Goal:
- Experience level:
- Training location:
- Equipment:
- Days per week:

## Weekly Training Plan
Day 1:
Day 2:
Day 3:
Day 4:
Day 5:
Day 6:
Day 7:

## Exercise Details
- Exercise
- Sets
- Reps
- Rest

## Progression Guidance
- Week-to-week progression rules

## Recovery Tips
- Sleep
- Rest
- Hydration
- Recovery pacing

## Optional Nutrition Guidance
- Protein
- Meals
- Hydration
- Calorie awareness
```

## JSON output skeleton

```json
{
  "goal_summary": {
    "goal": "",
    "experience_level": "beginner",
    "training_location": "",
    "equipment": [],
    "days_per_week": 0
  },
  "weekly_plan": [],
  "exercises": [
    {
      "name": "",
      "sets": 0,
      "reps": "",
      "rest_seconds": 0
    }
  ],
  "progression_guidance": [],
  "recovery_tips": [],
  "nutrition_guidance": []
}
```

## Limits

Do not:
- diagnose medical conditions,
- replace professional medical/coaching advice,
- prescribe extreme diets,
- recommend unsafe beginner intensity.

If user reports pain/injury/medical condition, keep guidance general and recommend qualified professional support.

## Author

Vassiliy Lakhonin
