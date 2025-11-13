import re
from typing import Match


def strong_password(password) -> Match[str] | None:
    """
    Check if a password meets strong password criteria.

    Args:
        password (str): The password to be checked.

    Returns:
        Match[str] | None: A match object if the password meets the criteria, None otherwise.
    """

    return re.search(
        r"^(?=[^A-Z]*[A-Z])(?=[^a-z]*[a-z])(?=\D*\d)(?=[^#?!@$%^&*-]*[#?!@$%^&*-]).{8,}$",
        password,
        re.I,
    )
