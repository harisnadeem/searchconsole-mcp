"""Tests for searchconsole_mcp/utils.py."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

import searchconsole_mcp.utils as utils


class TestGetCredentials:
    """Tests for get_credentials."""

    def test_get_credentials_uses_cache(self):
        """google.auth.default is called only once due to caching."""
        fake_creds = MagicMock()
        with (
            patch.object(utils, "_cached_credentials", None),
            patch(
                "searchconsole_mcp.utils.google.auth.default",
                return_value=(fake_creds, "demo-project"),
            ) as mock_default,
        ):
            first = utils.get_credentials()
            second = utils.get_credentials()

            assert first is fake_creds
            assert second is fake_creds
            assert mock_default.call_count == 1


class TestRefreshAccessToken:
    """Tests for _refresh_access_token."""

    def test_refreshes_when_not_valid(self):
        """Invalid credentials are refreshed and token is returned."""
        fake_creds = MagicMock()
        fake_creds.valid = False
        fake_creds.token = "fresh-token"

        with patch("searchconsole_mcp.utils.get_credentials", return_value=fake_creds):
            token = utils._refresh_access_token()

        fake_creds.refresh.assert_called_once()
        assert token == "fresh-token"

    def test_raises_when_token_missing(self):
        """Missing token raises a clear error."""
        fake_creds = MagicMock()
        fake_creds.valid = True
        fake_creds.token = None

        with (
            patch("searchconsole_mcp.utils.get_credentials", return_value=fake_creds),
            pytest.raises(RuntimeError, match="Failed to obtain an access token"),
        ):
            utils._refresh_access_token()


class TestGoogleBearerAuth:
    """Tests for _GoogleBearerAuth."""

    @pytest.mark.asyncio
    async def test_auth_flow_adds_bearer_token(self):
        """Authorization header is added on first request."""
        auth = utils._GoogleBearerAuth()
        request = httpx.Request("GET", "https://example.com")
        flow = auth.async_auth_flow(request)

        with patch("searchconsole_mcp.utils._refresh_access_token", return_value="abc123"):
            first_request = await flow.__anext__()
            assert first_request.headers["Authorization"] == "Bearer abc123"

            with pytest.raises(StopAsyncIteration):
                await flow.asend(httpx.Response(200, request=first_request))


class TestGetAuthenticatedClient:
    """Tests for get_authenticated_client."""

    @pytest.mark.asyncio
    async def test_client_configuration(self):
        """Client has expected base URL and default headers."""
        client = await utils.get_authenticated_client()
        try:
            assert str(client.base_url) == f"{utils.GSC_BASE_URL}/"
            assert client.headers["User-Agent"] == "searchconsole-mcp/0.1.0"
            assert client.headers["Accept"] == "application/json"
            assert isinstance(client.auth, utils._GoogleBearerAuth)
        finally:
            await client.aclose()
