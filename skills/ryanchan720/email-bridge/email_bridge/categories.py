"""Email category definitions for classification."""

from enum import Enum


class EmailCategory(str, Enum):
    """Predefined email categories for future classification."""
    VERIFICATION = "verification"  # Email verification codes, account confirmations
    SECURITY = "security"          # Security alerts, login notifications
    SUBSCRIPTION = "subscription"  # Newsletters, marketing emails
    SPAM_LIKE = "spam_like"        # Likely spam or low-priority
    NORMAL = "normal"              # Regular personal/business email


# Keywords for simple category detection (future: use ML/rule engine)
CATEGORY_KEYWORDS = {
    EmailCategory.VERIFICATION: [
        "验证码", "verify", "verification code", "确认", "activate",
        "activate your account", "confirmation"
    ],
    EmailCategory.SECURITY: [
        "安全", "security alert", "login attempt", "new login",
        "password change", "unusual activity", "账户安全"
    ],
    EmailCategory.SUBSCRIPTION: [
        "newsletter", "unsubscribe", "opt-out", "订阅", "退订",
        "weekly digest", "daily update"
    ],
    EmailCategory.SPAM_LIKE: [
        "winner", "congratulations", "click here now", "limited time",
        "act now", "免费", "优惠"
    ],
}


def detect_category(subject: str, body: str = "") -> EmailCategory:
    """Simple keyword-based category detection."""
    text = f"{subject} {body}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category
    return EmailCategory.NORMAL
