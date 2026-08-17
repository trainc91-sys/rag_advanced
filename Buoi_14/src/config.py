import os
from dotenv import load_dotenv

# Load .env file from buoi_14 root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

# Supported RBAC Roles
VALID_ROLES = ["Admin", "Risk_Manager", "HR", "Staff", "Guest"]

# Default role mapping for categorization rules
ROLE_CATEGORIES = {
    "HR": ["Admin", "HR"],
    "RISK": ["Admin", "Risk_Manager", "Staff"],
    "GENERAL": ["Admin", "Risk_Manager", "HR", "Staff", "Guest"]
}

def validate_roles(user_roles):
    """Validates user roles list against system valid roles."""
    if isinstance(user_roles, str):
        user_roles = [user_roles]
    validated = [r for r in user_roles if r in VALID_ROLES]
    return validated if validated else ["Guest"]
