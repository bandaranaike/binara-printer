"""Authentication for the local Electron-to-printer connection."""

import hmac
import os
from typing import Annotated

from fastapi import Header, HTTPException, status


TOKEN_ENVIRONMENT_VARIABLE = "PRINT_AGENT_TOKEN"
TOKEN_HEADER = "X-Print-Agent-Token"
MINIMUM_TOKEN_LENGTH = 32


def validate_security_configuration() -> None:
    """Fail closed when the printer agent has not been provisioned securely."""
    token = os.getenv(TOKEN_ENVIRONMENT_VARIABLE, "")
    if len(token) < MINIMUM_TOKEN_LENGTH:
        raise RuntimeError(
            f"{TOKEN_ENVIRONMENT_VARIABLE} must be set and contain at least "
            f"{MINIMUM_TOKEN_LENGTH} characters"
        )


def require_print_agent_token(
    supplied_token: Annotated[str | None, Header(alias=TOKEN_HEADER)] = None,
) -> None:
    """Require the per-machine secret on every print request."""
    expected_token = os.getenv(TOKEN_ENVIRONMENT_VARIABLE, "")
    if (
        not expected_token
        or not supplied_token
        or not hmac.compare_digest(supplied_token, expected_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
