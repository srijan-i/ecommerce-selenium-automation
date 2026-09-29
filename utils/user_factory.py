"""Generates a brand-new, never-used user for every run."""
import uuid
from datetime import datetime


def build_new_user(profile):
    """
    Returns a copy of the `new_user` profile with a unique e-mail address added.

    A unique e-mail per run is what removes the classic
    "email already exists / wrong old password" problem: the account this run
    registers is guaranteed not to exist yet, and the same credentials are then
    used for the login step.
    """
    prefix = str(profile.get("email_prefix") or "qa.user").strip()
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user = dict(profile)
    user["email"] = f"{prefix}.{stamp}.{uuid.uuid4().hex[:6]}@example.com"
    return user
