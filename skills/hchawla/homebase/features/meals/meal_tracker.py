#!/usr/bin/env python3
"""
Kids Meal Tracker
Tracks what kids ate and suggests next meals based on history and config rules.
"""

import json
import os
import sys
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from utils import write_json_atomic


def parse_rule_items(rule: str) -> List[str]:
    """Extract food items from a rule string like 'Breakfast: eggs, oats, toast'."""
    if ":" in rule:
        _, items_str = rule.split(":", 1)
    else:
        items_str = rule
    import re
    items = [i.strip() for i in items_str.split(",") if i.strip()]
    return [re.sub(r"^(?:or|and)\s+", "", i) for i in items]


class MealTracker:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.data_path = os.path.join(base_path, "household")
        os.makedirs(self.data_path, exist_ok=True)
        self.history_file = os.path.join(self.data_path, "meal_history.json")
        self.history = self._load()
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        try:
            from core.config_loader import config
            return config
        except Exception:
            return {}

    def _load(self) -> Dict:
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {}

    def _save(self):
        write_json_atomic(self.history_file, self.history)

    # ─── Log what was eaten ──────────────────────────────────────────────────

    def log_meal(self, child: str, meal_type: str, food: str, date: str = None):
        """Log what a child ate."""
        child = child.lower()
        if child not in self.history:
            self.history[child] = []

        entry = {
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "meal_type": meal_type,
            "food": food,
            "logged_at": datetime.now().isoformat()
        }
        self.history[child].append(entry)

        # Keep only last 30 days
        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.history[child] = [
            e for e in self.history[child]
            if e.get("date", "") >= cutoff
        ]
        self._save()

    def get_recent_meals(self, child: str, meal_type: str, days: int = 5) -> List[str]:
        """Get what a child ate for a specific meal type in the last N days."""
        child = child.lower()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return [
            e["food"] for e in self.history.get(child, [])
            if e.get("meal_type") == meal_type and e.get("date", "") >= cutoff
        ]

    def had_eggs_today(self, child: str) -> bool:
        """Check if child had eggs at breakfast today."""
        today = datetime.now().strftime("%Y-%m-%d")
        for entry in self.history.get(child.lower(), []):
            if (entry.get("date") == today and
                    entry.get("meal_type") == "breakfast" and
                    "egg" in entry.get("food", "").lower()):
                return True
        return False

    # ─── Suggest next meal ───────────────────────────────────────────────────

    def _parse_rule_items(self, rule: str) -> List[str]:
        return parse_rule_items(rule)

    def get_meal_suggestions(self) -> Dict:
        """
        Return concrete meal suggestions based on config rules and history.
        Rules come from config.json kids[].meal_rules — no hardcoded names.
        """
        kids = self.config.kids if hasattr(self.config, "kids") else []
        suggestions = {}
        for kid in kids:
            name = kid.name.lower()
            had_eggs = self.had_eggs_today(name)
            rules = kid.meal_rules if hasattr(kid, "meal_rules") else []

            breakfast_options = []
            lunch_options = []
            side_options = ["Fruit"]
            no_rules = []

            for rule in rules:
                rl = rule.lower()
                if rl.startswith("breakfast:"):
                    breakfast_options = self._parse_rule_items(rule)
                elif rl.startswith("lunch:"):
                    lunch_options = self._parse_rule_items(rule)
                elif rl.startswith("sides:") or rl.startswith("side:"):
                    side_options = self._parse_rule_items(rule)
                elif rl.startswith("no "):
                    no_rules.append(rl)

            # Pick breakfast, avoiding recent repeats
            if breakfast_options:
                recent = self.get_recent_meals(name, "breakfast", days=3)
                available = [o for o in breakfast_options if o not in recent]
                breakfast = random.choice(available if available else breakfast_options)
            else:
                breakfast = "TBD"

            # Pick lunch, applying NO-egg rules
            if lunch_options:
                filtered = lunch_options[:]
                if had_eggs or "egg" in breakfast.lower():
                    for no_rule in no_rules:
                        if "egg" in no_rule and "lunch" in no_rule:
                            filtered = [o for o in filtered if "egg" not in o.lower()]
                lunch = random.choice(filtered if filtered else lunch_options)
            else:
                lunch = "TBD"

            side = random.choice(side_options) if side_options else "Fruit"

            note = ""
            if had_eggs:
                for no_rule in no_rules:
                    if "egg" in no_rule and "lunch" in no_rule:
                        note = "Had eggs for breakfast today."
                        break

            suggestions[name] = {
                "name": kid.name,
                "breakfast": breakfast,
                "lunch": lunch,
                "side": side,
                "note": note,
            }
        return suggestions

    def format_for_whatsapp(self, suggestions: Dict) -> str:
        """Format raw config/history into a helper message for the agent."""
        lines = ["🍽️ *Meal Rule Context*\n"]
        for key, data in suggestions.items():
            lines.append(f"*{data['name']}*")
            lines.append(f"  • Rules: {', '.join(data['rules'][:2])}...")
            if data['had_eggs_breakfast']:
                lines.append("  • ⚠️ Had eggs for breakfast today.")
            lines.append("")
        return "\n".join(lines)


if __name__ == "__main__":
    import sys
    tracker = MealTracker("skills/homebase")

    if len(sys.argv) > 1 and sys.argv[1] == "log":
        # Usage: meal_tracker.py log <kid_key> <meal_type> "<food>"
        if len(sys.argv) >= 5:
            tracker.log_meal(sys.argv[2], sys.argv[3], sys.argv[4])
            print(f"Logged: {sys.argv[2]} had {sys.argv[4]} for {sys.argv[3]}")
    else:
        suggestions = tracker.get_meal_suggestions()
        print(tracker.format_for_whatsapp(suggestions))