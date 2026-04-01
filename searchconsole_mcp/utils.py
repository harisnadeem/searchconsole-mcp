"""Shared utilities for the Search Console MCP server.

Uses google-auth for Application Default Credentials (ADC) and httpx for
async HTTP calls. Token refresh is handled automatically via httpx's
auth flow (including 401 retry).
"""

import google.auth
import google.auth.transport.requests as google_requests
import httpx

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
GSC_BASE_URL = "https://www.searchconsole.googleapis.com/webmasters/v3"

_cached_credentials: google.auth.credentials.Credentials | None = None


def get_credentials() -> google.auth.credentials.Credentials:
    """Return Application Default Credentials with GSC scope.

    Uses `gcloud auth application-default login` or
    GOOGLE_APPLICATION_CREDENTIALS (service account JSON key).
    """
    global _cached_credentials
    if _cached_credentials is None:
        credentials, _ = google.auth.default(scopes=SCOPES)
        _cached_credentials = credentials
    return _cached_credentials


def _refresh_access_token() -> str:
    """Force-refresh credentials and return the current access token."""
    creds = get_credentials()
    if not creds.valid:
        request = google_requests.Request()
        creds.refresh(request)
    token = creds.token
    if not token:
        raise RuntimeError(
            "Failed to obtain an access token. "
            "Run 'gcloud auth application-default login' or set "
            "GOOGLE_APPLICATION_CREDENTIALS."
        )
    return token


class _GoogleBearerAuth(httpx.Auth):
    """httpx async auth that injects a Google Bearer token and handles refresh.

    On each request the Authorization header is set. If the response is 401,
    the token is refreshed and the request is retried once.
    """

    requires_response_body = True

    def __init__(self) -> None:
        super().__init__()
        self._token: str | None = None

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> "httpx._types.AsyncIterator[httpx.Response]":
        # Set token on request
        if not self._token:
            self._token = _refresh_access_token()
        request.headers["Authorization"] = f"Bearer {self._token}"

        response = yield request

        # Retry once on 401 — token may have expired
        if response.status_code == 401:
            self._token = _refresh_access_token()
            request.headers["Authorization"] = f"Bearer {self._token}"
            yield request


async def get_authenticated_client() -> httpx.AsyncClient:
    """Return an httpx AsyncClient with valid GSC credentials.

    The client handles token refresh automatically via _GoogleBearerAuth.
    """
    return httpx.AsyncClient(
        base_url=GSC_BASE_URL,
        auth=_GoogleBearerAuth(),
        timeout=60.0,
        headers={
            "User-Agent": "searchconsole-mcp/0.1.0",
            "Accept": "application/json",
        },
    )
