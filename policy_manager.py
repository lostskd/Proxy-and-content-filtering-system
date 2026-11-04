import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_POLICY_FILE = BASE_DIR / "policies.json"


def load_policies(policy_file=DEFAULT_POLICY_FILE):
    """Load filtering policies from JSON."""
    with open(policy_file, "r") as file:
        return json.load(file)


def is_allowed(request, policies=None):
    """Check whether a request is allowed."""

    if policies is None:
        policies = load_policies()

    request = request.lower()

    for keyword in policies.get("blocked_keywords", []):
        if keyword.lower() in request:
            return False

    for path in policies.get("blocked_paths", []):
        if path.lower() in request:
            return False

    return policies.get("default_action", "ALLOW").upper() == "ALLOW"


if __name__ == "__main__":
    policies = load_policies()

    print("===== POLICY MANAGER TEST =====")

    for request in ["/news", "/gambling", "/malware", "/education", "/phishing"]:
        result = "ALLOWED" if is_allowed(request, policies) else "BLOCKED"
        print(f"{request}: {result}")
