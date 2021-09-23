"""Service logic for black token."""

from src.chat.model.token_blacklist import BlacklistedToken
from src.chat.service import save_data


def save_token_into_blacklist(token: str) -> None:
    """Save the token into blacklist."""

    blacklist_token = BlacklistedToken(token=token)
    # insert the token
    save_data(blacklist_token)


def check_blacklist(auth_token) -> bool:
    """Check whether auth token has been blacklisted."""

    return BlacklistedToken.query.filter_by(token=str(auth_token)).first() is not None
