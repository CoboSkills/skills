"""
Tests for config-driven features introduced by the config purge refactor.
Covers: parse_rule_items, config-driven meal suggestions, Kid.emoji_char,
_tracked_names, Config.app_name/owner_phone.
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from conftest import MINIMAL_CONFIG


# ── Config accessor tests ────────────────────────────────────────────────────

class TestConfigAccessors:

    def test_app_name_from_config(self, tmp_skill_dir):
        from core.config_loader import Config
        cfg = Config({**MINIMAL_CONFIG, "app": {"name": "Test Homebase"}})
        assert cfg.app_name == "Test Homebase"

    def test_app_name_default(self, tmp_skill_dir):
        from core.config_loader import Config
        cfg = Config({})
        assert cfg.app_name == "Homebase"

    def test_owner_phone(self, tmp_skill_dir):
        from core.config_loader import Config
        cfg = Config({**MINIMAL_CONFIG, "app": {"owner_phone": "+15551234567"}})
        assert cfg.owner_phone == "+15551234567"

    def test_owner_phone_default_empty(self, tmp_skill_dir):
        from core.config_loader import Config
        cfg = Config({})
        assert cfg.owner_phone == ""


# ── Kid emoji tests ──────────────────────────────────────────────────────────

class TestKidEmoji:

    def test_girl_emoji(self, tmp_skill_dir):
        from core.config_loader import Kid
        kid = Kid({"name": "Alice", "emoji": "girl"})
        assert kid.emoji_char == "\U0001F467"  # 👧

    def test_boy_emoji(self, tmp_skill_dir):
        from core.config_loader import Kid
        kid = Kid({"name": "Bob", "emoji": "boy"})
        assert kid.emoji_char == "\U0001F466"  # 👦

    def test_unknown_emoji_fallback(self, tmp_skill_dir):
        from core.config_loader import Kid
        kid = Kid({"name": "Pat", "emoji": "other"})
        assert kid.emoji_char == "\U0001F9D2"  # 🧒

    def test_missing_emoji_fallback(self, tmp_skill_dir):
        from core.config_loader import Kid
        kid = Kid({"name": "Pat"})
        assert kid.emoji == "child"
        assert kid.emoji_char == "\U0001F9D2"


# ── parse_rule_items tests ───────────────────────────────────────────────────

class TestParseRuleItems:

    def test_with_colon(self, tmp_skill_dir):
        from features.meals.meal_tracker import parse_rule_items
        result = parse_rule_items("Breakfast: Scrambled eggs, oats, jam toast")
        assert result == ["Scrambled eggs", "oats", "jam toast"]

    def test_without_colon(self, tmp_skill_dir):
        from features.meals.meal_tracker import parse_rule_items
        result = parse_rule_items("Scrambled eggs, oats, jam toast")
        assert result == ["Scrambled eggs", "oats", "jam toast"]

    def test_empty_items_filtered(self, tmp_skill_dir):
        from features.meals.meal_tracker import parse_rule_items
        result = parse_rule_items("Breakfast: eggs, , toast, ")
        assert result == ["eggs", "toast"]

    def test_single_item(self, tmp_skill_dir):
        from features.meals.meal_tracker import parse_rule_items
        result = parse_rule_items("Lunch: Khichdi")
        assert result == ["Khichdi"]


# ── Config-driven meal suggestions ───────────────────────────────────────────

class TestConfigDrivenMealSuggestions:

    def test_returns_suggestions_for_all_configured_kids(self, tmp_skill_dir):
        from features.meals.meal_tracker import MealTracker
        tracker = MealTracker(str(tmp_skill_dir))
        suggestions = tracker.get_meal_suggestions()
        assert "amyra" in suggestions
        assert "reyansh" in suggestions

    def test_breakfast_from_config_rules(self, tmp_skill_dir):
        from features.meals.meal_tracker import MealTracker
        tracker = MealTracker(str(tmp_skill_dir))
        suggestions = tracker.get_meal_suggestions()
        amyra = suggestions["amyra"]
        # Breakfast should be one of the options from config rules
        valid_options = ["Scrambled eggs", "oats", "jam toast", "Dalia", "Indian breakfast items"]
        assert amyra["breakfast"] in valid_options

    def test_lunch_from_config_rules(self, tmp_skill_dir):
        from features.meals.meal_tracker import MealTracker
        tracker = MealTracker(str(tmp_skill_dir))
        suggestions = tracker.get_meal_suggestions()
        amyra = suggestions["amyra"]
        valid_options = ["Cheese sandwich", "bread jam", "egg bites"]
        assert amyra["lunch"] in valid_options

    def test_egg_rule_filtering(self, tmp_skill_dir):
        """When kid had eggs at breakfast, egg items must not appear at lunch."""
        from features.meals.meal_tracker import MealTracker
        tracker = MealTracker(str(tmp_skill_dir))
        # Log eggs for breakfast today
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        tracker.log_meal("amyra", "breakfast", "Scrambled eggs", today)

        # Run suggestions multiple times to check egg filtering
        for _ in range(20):
            suggestions = tracker.get_meal_suggestions()
            amyra = suggestions["amyra"]
            assert "egg" not in amyra["lunch"].lower(), \
                f"Egg item '{amyra['lunch']}' appeared at lunch after eggs for breakfast"

    def test_sides_from_config(self, tmp_skill_dir):
        from features.meals.meal_tracker import MealTracker
        tracker = MealTracker(str(tmp_skill_dir))
        suggestions = tracker.get_meal_suggestions()
        amyra = suggestions["amyra"]
        valid_sides = ["Fruit", "roasted chana", "makhana"]
        assert amyra["side"] in valid_sides

    def test_empty_rules_returns_tbd(self, tmp_skill_dir):
        """Kid with no meal_rules gets TBD suggestions."""
        from features.meals.meal_tracker import MealTracker
        from core.config_loader import Config
        empty_config = Config({
            "family": {"kids": [{"name": "NoRules", "meal_rules": []}]}
        })
        tracker = MealTracker(str(tmp_skill_dir))
        tracker.config = empty_config
        suggestions = tracker.get_meal_suggestions()
        assert suggestions["norules"]["breakfast"] == "TBD"
        assert suggestions["norules"]["lunch"] == "TBD"

    def test_kid_name_preserved(self, tmp_skill_dir):
        from features.meals.meal_tracker import MealTracker
        tracker = MealTracker(str(tmp_skill_dir))
        suggestions = tracker.get_meal_suggestions()
        assert suggestions["amyra"]["name"] == "Amyra"
        assert suggestions["reyansh"]["name"] == "Reyansh"


# ── _tracked_names tests ─────────────────────────────────────────────────────

class TestTrackedNames:

    def test_returns_configured_names(self, tmp_skill_dir):
        from features.health import health_tracker as ht
        names = ht._tracked_names()
        assert "Amyra" in names
        assert "Reyansh" in names

    def test_empty_config_returns_message(self, tmp_skill_dir):
        from features.health import health_tracker as ht
        with patch.object(ht, "_load_cfg", return_value={"children": {}}):
            names = ht._tracked_names()
            assert names == "no children configured"
