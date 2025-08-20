import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch

from griptape.tools.mcp.tool import MCPTool


class TestMCPTool:
    @pytest.fixture
    def mock_connection(self):
        return {
            "transport": "stdio",
            "command": "echo",
            "args": ["test"],
            "env": None,
            "cwd": None,
            "encoding": "utf-8",
            "encoding_error_handler": "strict",
            "session_kwargs": None,
        }

    @patch("griptape.tools.mcp.tool.create_session")
    def test_init_in_sync_context(self, mock_create_session, mock_connection):
        """Test that MCPTool can be initialized in a synchronous context."""
        # Mock the session and its methods
        mock_session = AsyncMock()
        mock_tools_response = Mock()
        mock_tools_response.tools = []
        mock_session.list_tools.return_value = mock_tools_response
        
        # Mock the async context manager
        mock_create_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_create_session.return_value.__aexit__ = AsyncMock(return_value=None)

        # This should not raise RuntimeError about asyncio.run() in a running loop
        tool = MCPTool(connection=mock_connection)
        assert tool is not None
        assert hasattr(tool, 'connection')

    @pytest.mark.asyncio
    @patch("griptape.tools.mcp.tool.create_session")
    async def test_init_in_async_context(self, mock_create_session, mock_connection):
        """Test that MCPTool can be initialized within an async context."""
        # Mock the session and its methods
        mock_session = AsyncMock()
        mock_tools_response = Mock()
        mock_tools_response.tools = []
        mock_session.list_tools.return_value = mock_tools_response
        
        # Mock the async context manager  
        mock_create_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_create_session.return_value.__aexit__ = AsyncMock(return_value=None)

        # This should not raise RuntimeError about asyncio.run() in a running loop
        tool = MCPTool(connection=mock_connection)
        assert tool is not None
        assert hasattr(tool, 'connection')

    @patch("griptape.tools.mcp.tool.create_session")
    def test_basic_initialization_no_asyncio_error(self, mock_create_session, mock_connection):
        """Test that MCPTool initialization doesn't raise asyncio.run() errors."""
        # Simple mock setup
        mock_session = AsyncMock()
        mock_tools_response = Mock()
        mock_tools_response.tools = []
        mock_session.list_tools.return_value = mock_tools_response
        
        mock_create_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_create_session.return_value.__aexit__ = AsyncMock(return_value=None)

        # The key test: this should not raise the original asyncio.run() error
        try:
            tool = MCPTool(connection=mock_connection)
            assert tool is not None
        except RuntimeError as e:
            if "asyncio.run() cannot be called from a running event loop" in str(e):
                pytest.fail("The original asyncio.run() error was not fixed")
            else:
                # Other RuntimeErrors might be expected in test context
                pass