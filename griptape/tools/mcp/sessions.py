from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypedDict

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path

    import httpx
    from mcp import ClientSession  # type: ignore[reportAttributeAccessIssue]

EncodingErrorHandler = Literal["strict", "ignore", "replace"]

DEFAULT_ENCODING = "utf-8"
DEFAULT_ENCODING_ERROR_HANDLER: EncodingErrorHandler = "strict"

DEFAULT_HTTP_TIMEOUT = 5
DEFAULT_SSE_READ_TIMEOUT = 60 * 5

DEFAULT_STREAMABLE_HTTP_TIMEOUT = timedelta(seconds=30)
DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT = timedelta(seconds=60 * 5)


class McpHttpClientFactory(Protocol):
    def __call__(
        self,
        headers: dict[str, str] | None = None,
        timeout: httpx.Timeout | None = None,
        auth: httpx.Auth | None = None,
    ) -> httpx.AsyncClient: ...


class StdioConnection(TypedDict):
    transport: Literal["stdio"]

    command: str
    """The executable to run to start the server."""

    args: list[str]
    """Command line arguments to pass to the executable."""

    env: dict[str, str] | None
    """The environment to use when spawning the process."""

    cwd: str | Path | None
    """The working directory to use when spawning the process."""

    encoding: str
    """The text encoding used when sending/receiving messages to the server."""

    encoding_error_handler: EncodingErrorHandler
    """
    The text encoding error handler.

    See https://docs.python.org/3/library/codecs.html#codec-base-classes for
    explanations of possible values.
    """

    session_kwargs: dict[str, Any] | None
    """Additional keyword arguments to pass to the ClientSession."""


class SSEConnection(TypedDict):
    transport: Literal["sse"]

    url: str
    """The URL of the SSE endpoint to connect to."""

    headers: dict[str, Any] | None
    """HTTP headers to send to the SSE endpoint."""

    timeout: float
    """HTTP timeout."""

    sse_read_timeout: float
    """SSE read timeout."""

    session_kwargs: dict[str, Any] | None
    """Additional keyword arguments to pass to the ClientSession."""

    httpx_client_factory: McpHttpClientFactory | None
    """Custom factory for httpx.AsyncClient (optional)."""


class StreamableHttpConnection(TypedDict):
    transport: Literal["streamable_http"]

    url: str
    """The URL of the endpoint to connect to."""

    headers: dict[str, Any] | None
    """HTTP headers to send to the endpoint."""

    timeout: timedelta
    """HTTP timeout."""

    sse_read_timeout: timedelta
    """How long (in seconds) the client will wait for a new event before disconnecting.
    All other HTTP operations are controlled by `timeout`."""

    terminate_on_close: bool
    """Whether to terminate the session on close."""

    session_kwargs: dict[str, Any] | None
    """Additional keyword arguments to pass to the ClientSession."""

    httpx_client_factory: McpHttpClientFactory | None
    """Custom factory for httpx.AsyncClient (optional)."""


class WebsocketConnection(TypedDict):
    transport: Literal["websocket"]

    url: str
    """The URL of the Websocket endpoint to connect to."""

    session_kwargs: dict[str, Any] | None
    """Additional keyword arguments to pass to the ClientSession"""


Connection = StdioConnection | SSEConnection | StreamableHttpConnection | WebsocketConnection  # type: ignore[reportGeneralTypeIssues]


@asynccontextmanager
async def _create_stdio_session(
    *,
    command: str,
    args: list[str],
    env: dict[str, str] | None = None,
    cwd: str | Path | None = None,
    encoding: str = DEFAULT_ENCODING,
    encoding_error_handler: Literal["strict", "ignore", "replace"] = DEFAULT_ENCODING_ERROR_HANDLER,
    session_kwargs: dict[str, Any] | None = None,
) -> AsyncIterator[ClientSession]:
    """Create a new session to an MCP server using stdio.

    Args:
        command: Command to execute
        args: Arguments for the command
        env: Environment variables for the command
        cwd: Working directory for the command
        encoding: Character encoding
        encoding_error_handler: How to handle encoding errors
        session_kwargs: Additional keyword arguments to pass to the ClientSession
    """
    from mcp import ClientSession, StdioServerParameters  # type: ignore[reportAttributeAccessIssue]
    from mcp.client.stdio import stdio_client  # type: ignore[reportMissingImports]

    # NOTE: execution commands (e.g., `uvx` / `npx`) require PATH envvar to be set.
    # To address this, we automatically inject existing PATH envvar into the `env` value,
    # if it's not already set.
    env = env or {}
    if "PATH" not in env:
        env["PATH"] = os.environ.get("PATH", "")

    server_params = StdioServerParameters(
        command=command,
        args=args,
        env=env,
        cwd=cwd,
        encoding=encoding,
        encoding_error_handler=encoding_error_handler,
    )

    # Create and store the connection
    async with stdio_client(server_params) as (read, write):  # noqa: SIM117
        async with ClientSession(read, write, **(session_kwargs or {})) as session:
            yield session


@asynccontextmanager
async def _create_sse_session(
    *,
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: float = DEFAULT_HTTP_TIMEOUT,
    sse_read_timeout: float = DEFAULT_SSE_READ_TIMEOUT,
    session_kwargs: dict[str, Any] | None = None,
    httpx_client_factory: McpHttpClientFactory | None = None,
) -> AsyncIterator[ClientSession]:
    """Create a new session to an MCP server using SSE.

    Args:
        url: URL of the SSE server
        headers: HTTP headers to send to the SSE endpoint
        timeout: HTTP timeout
        sse_read_timeout: SSE read timeout
        session_kwargs: Additional keyword arguments to pass to the ClientSession
        httpx_client_factory: Custom factory for httpx.AsyncClient (optional)
    """
    from mcp import ClientSession  # type: ignore[reportAttributeAccessIssue]
    from mcp.client.sse import sse_client  # type: ignore[reportMissingImports]

    # Create and store the connection
    kwargs = {}
    if httpx_client_factory is not None:
        kwargs["httpx_client_factory"] = httpx_client_factory

    async with sse_client(url, headers, timeout, sse_read_timeout, **kwargs) as (read, write):  # noqa: SIM117
        async with ClientSession(read, write, **(session_kwargs or {})) as session:
            yield session


@asynccontextmanager
async def _create_streamable_http_session(
    *,
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: timedelta = DEFAULT_STREAMABLE_HTTP_TIMEOUT,
    sse_read_timeout: timedelta = DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT,
    terminate_on_close: bool = True,
    session_kwargs: dict[str, Any] | None = None,
    httpx_client_factory: McpHttpClientFactory | None = None,
) -> AsyncIterator[ClientSession]:
    """Create a new session to an MCP server using Streamable HTTP.

    Args:
        url: URL of the endpoint to connect to
        headers: HTTP headers to send to the endpoint
        timeout: HTTP timeout
        sse_read_timeout: How long (in seconds) the client will wait for a new event before disconnecting
        terminate_on_close: Whether to terminate the session on close
        session_kwargs: Additional keyword arguments to pass to the ClientSession
        httpx_client_factory: Custom factory for httpx.AsyncClient (optional)
    """
    from mcp import ClientSession  # type: ignore[reportAttributeAccessIssue]
    from mcp.client.streamable_http import streamablehttp_client  # type: ignore[reportMissingImports]

    # Create and store the connection
    kwargs = {}
    if httpx_client_factory is not None:
        kwargs["httpx_client_factory"] = httpx_client_factory

    async with streamablehttp_client(url, headers, timeout, sse_read_timeout, terminate_on_close, **kwargs) as (  # noqa: SIM117
        read,
        write,
        _,
    ):
        async with ClientSession(read, write, **(session_kwargs or {})) as session:
            yield session


@asynccontextmanager
async def _create_websocket_session(
    *,
    url: str,
    session_kwargs: dict[str, Any] | None = None,
) -> AsyncIterator[ClientSession]:
    """Create a new session to an MCP server using Websockets.

    Args:
        url: URL of the Websocket endpoint
        session_kwargs: Additional keyword arguments to pass to the ClientSession
    """
    from mcp import ClientSession  # type: ignore[reportAttributeAccessIssue]
    from mcp.client.websocket import websocket_client  # type: ignore[reportMissingImports]

    async with websocket_client(url) as (read, write):  # noqa: SIM117
        async with ClientSession(read, write, **(session_kwargs or {})) as session:
            yield session


@asynccontextmanager
async def create_session(  # noqa: C901
    connection: Connection,
) -> AsyncIterator[ClientSession]:
    """Create a new session to an MCP server.

    Args:
        connection: Connection config to use to connect to the server

    Raises:
        ValueError: If transport is not recognized
        ValueError: If required parameters for the specified transport are missing

    Yields:
        A ClientSession
    """
    transport = connection["transport"]
    if transport == "sse":
        if "url" not in connection:
            raise ValueError("'url' parameter is required for SSE connection")
        timeout_val = connection.get("timeout", DEFAULT_HTTP_TIMEOUT)
        if isinstance(timeout_val, timedelta):
            timeout_val = timeout_val.total_seconds()
        sse_read_timeout_val = connection.get("timeout", DEFAULT_HTTP_TIMEOUT)
        if isinstance(sse_read_timeout_val, timedelta):
            sse_read_timeout_val = sse_read_timeout_val.total_seconds()
        async with _create_sse_session(
            url=connection["url"],
            headers=connection.get("headers"),
            timeout=timeout_val,
            sse_read_timeout=sse_read_timeout_val,
            session_kwargs=connection.get("session_kwargs"),
            httpx_client_factory=connection.get("httpx_client_factory"),
        ) as session:
            yield session
    elif transport == "streamable_http":
        if "url" not in connection:
            raise ValueError("'url' parameter is required for Streamable HTTP connection")
        timeout_val = connection.get("timeout", DEFAULT_STREAMABLE_HTTP_TIMEOUT)
        if isinstance(timeout_val, (int, float)):
            timeout_val = timedelta(seconds=timeout_val)
        sse_read_timeout_val = connection.get("sse_read_timeout", DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT)
        if isinstance(sse_read_timeout_val, (int, float)):
            sse_read_timeout_val = timedelta(seconds=sse_read_timeout_val)
        async with _create_streamable_http_session(
            url=connection["url"],
            headers=connection.get("headers"),
            timeout=timeout_val,
            sse_read_timeout=sse_read_timeout_val,
            session_kwargs=connection.get("session_kwargs"),
            httpx_client_factory=connection.get("httpx_client_factory"),
        ) as session:
            yield session
    elif transport == "stdio":
        if "command" not in connection:
            raise ValueError("'command' parameter is required for stdio connection")
        async with _create_stdio_session(
            command=connection["command"],
            args=connection["args"],
            env=connection.get("env"),
            cwd=connection.get("cwd"),
            encoding=connection.get("encoding", DEFAULT_ENCODING),
            encoding_error_handler=connection.get("encoding_error_handler", DEFAULT_ENCODING_ERROR_HANDLER),
            session_kwargs=connection.get("session_kwargs"),
        ) as session:
            yield session
    elif transport == "websocket":
        if "url" not in connection:
            raise ValueError("'url' parameter is required for Websocket connection")
        async with _create_websocket_session(
            url=connection["url"],
            session_kwargs=connection.get("session_kwargs"),
        ) as session:
            yield session
    else:
        raise ValueError(
            f"Unsupported transport: {transport}. Must be one of: 'stdio', 'sse', 'websocket', 'streamable_http'"
        )
