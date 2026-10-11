"""Contract tests for the Apprise integration provider (no network — apprise.notify is stubbed)."""

import logging

import apprise
import pytest
from marvin_integration_sdk import CATEGORY_NOTIFY, INTEGRATION_REGISTRY, IntegrationContext, load_guide
from marvin_integration_sdk.testing import IntegrationContract

import marvin_integration_apprise  # noqa: F401 — registers the provider on import
from marvin_integration_apprise import AppriseProvider
from marvin_integration_apprise.provider import _parse_urls
from marvin_integration_apprise.recipes import DELIVERY_KEY


def _ctx(secret):
    return IntegrationContext(config={}, secret=secret, logger=logging.getLogger("test"), http=None)


def test_provider_registers_under_its_slug():
    assert "apprise" in INTEGRATION_REGISTRY
    assert INTEGRATION_REGISTRY["apprise"].category == CATEGORY_NOTIFY
    info = AppriseProvider().info()
    assert info["slug"] == "apprise"
    assert any(a["key"] == "notify" and a["capability"] == "notify" for a in info["actions"])


def test_parse_urls_splits_on_newline_and_comma():
    assert _parse_urls("json://a\njson://b") == ["json://a", "json://b"]
    assert _parse_urls("json://a, json://b") == ["json://a", "json://b"]
    assert _parse_urls("") == []
    assert _parse_urls(None) == []


def test_check_flags_missing_and_invalid_urls():
    p = AppriseProvider()
    assert p.check(_ctx(None))[0] == "unconfigured"
    assert p.check(_ctx("json://localhost"))[0] == "ok"
    status, err = p.check(_ctx("not-a-real-scheme://"))
    assert status == "error" and "Invalid" in err


def test_notify_sends_to_all_urls(monkeypatch):
    calls = {}

    def fake_notify(self, body="", title="", **kw):
        calls["body"], calls["title"], calls["targets"] = body, title, len(self)
        return True

    monkeypatch.setattr(apprise.Apprise, "notify", fake_notify)

    p = AppriseProvider()
    result = p.run_action("notify", {"title": "Entry Published", "body": "Hello"}, _ctx("json://a\njson://b"))
    assert result == {"sent": True, "targets": 2}
    assert calls["title"] == "Entry Published" and calls["body"] == "Hello" and calls["targets"] == 2


def test_notify_requires_a_configured_url():
    with pytest.raises(ValueError):
        AppriseProvider().run_action("notify", {"body": "x"}, _ctx(None))


def test_unknown_action_raises():
    with pytest.raises(NotImplementedError):
        AppriseProvider().run_action("nope", {}, _ctx("json://a"))


# ── what Apprise teaches Marvin (SDK 0.9.0) ──────────────────────────────────


class TestAppriseContract(IntegrationContract):
    @pytest.fixture
    def provider(self):
        return AppriseProvider()


def test_the_guide_ships_with_the_package():
    guide = load_guide(AppriseProvider)
    assert guide.startswith("# Apprise") and "one URL per line" in guide and "sent: false" in guide


def test_the_announce_recipe_records_whether_apprise_delivered_it():
    (recipe,) = AppriseProvider.recipes
    assert recipe.id == "announce-and-record-delivery"
    announce, sent, failed = recipe.definition["actions"]
    assert (announce["id"], announce["action"], announce["integration"]) == ("announce", "notify", "{{apprise_integration}}")
    assert announce["args"]["body"] == "${entry.title}\n${entry.url}"  # run-time templates, filled when it runs
    # Opposite `when`s on the notify step's own result make an if/else; notify reports a refusal as sent=False, not an error.
    assert sent["when"] == {"field": "steps.announce.output.sent", "op": "eq", "value": True}
    assert failed["when"] == {"field": "steps.announce.output.sent", "op": "eq", "value": False}
    assert (sent["metadata"], failed["metadata"]) == ({DELIVERY_KEY: "sent"}, {DELIVERY_KEY: "failed"})
