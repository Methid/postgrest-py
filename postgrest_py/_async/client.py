from typing import Dict, Optional, Union

from deprecation import deprecated
from httpx import BasicAuth, Response

from postgrest_py.__version__ import __version__
from postgrest_py.config import DEFAULT_POSTGREST_CLIENT_HEADERS
from postgrest_py.utils import AsyncClient

from .request_builder import AsyncRequestBuilder


class AsyncPostgrestClient:
    """PostgREST client."""

    def __init__(
        self,
        base_url: str,
        *,
        schema: str = "public",
        headers: Dict[str, str] = DEFAULT_POSTGREST_CLIENT_HEADERS,
    ) -> None:
        headers = {
            **headers,
            "Accept-Profile": schema,
            "Content-Profile": schema,
        }
        self.session = AsyncClient(base_url=base_url, headers=headers)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self.session.aclose()

    def auth(
        self,
        token: Optional[str],
        *,
        username: Union[str, bytes, None] = None,
        password: Union[str, bytes] = "",
    ):
        """
        Authenticate the client with either bearer token or basic authentication.

        Raise `ValueError` if neither authentication scheme is provided.
        Bearer token is preferred if both ones are provided.
        """
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        elif username:
            self.session.auth = BasicAuth(username, password)
        else:
            raise ValueError(
                "Neither bearer token or basic authentication scheme is provided"
            )
        return self

    def schema(self, schema: str):
        """Switch to another schema."""
        self.session.headers.update({"Accept-Profile": schema, "Content-Profile": schema})
        return self

    def from_(self, table: str) -> AsyncRequestBuilder:
        """Perform a table operation."""
        return AsyncRequestBuilder(self.session, f"/{table}")

    @deprecated("0.2.0", "1.0.0", __version__, "Use PostgrestClient.from_() instead")
    def from_table(self, table: str) -> AsyncRequestBuilder:
        """Alias to Self.from_()."""
        return self.from_(table)

    async def rpc(self, func: str, params: dict) -> Response:
        """Perform a stored procedure call."""
        path = f"/rpc/{func}"
        return await self.session.post(path, json=params)
