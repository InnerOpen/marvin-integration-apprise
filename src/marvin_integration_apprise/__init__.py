"""Apprise notifications as a Marvin integration provider.

Apprise (github.com/caronc/apprise) fans one message out to 100+ services — Slack, Discord, Telegram,
email, and more — through a single URL scheme. Wraps it as a Marvin ``notify`` provider: the Apprise
URL(s) are the credential (behind ``secret_ref``), and a ``notify`` action sends a title/body.
"""

from .provider import AppriseProvider

__all__ = ["AppriseProvider"]
__version__ = "0.1.0"
