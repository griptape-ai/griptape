"""
Figma Integration Module

Provides Figma API integration specifically for Maya Patel (The Interface).
Enables design system synchronization, asset export, and design file management.

Note: This integration is ONLY used by Maya Patel. Other leadership bots
do not have Figma access.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


@dataclass
class FigmaFile:
    """Represents a Figma design file."""

    key: str
    name: str
    last_modified: datetime
    thumbnail_url: str | None = None
    version: str | None = None


@dataclass
class FigmaComponent:
    """Represents a Figma component in the design system."""

    component_id: str
    name: str
    description: str | None
    component_set_id: str | None
    created_at: datetime | None


@dataclass
class DesignToken:
    """Represents a design token (color, spacing, typography, etc.)."""

    token_name: str
    token_type: str  # color, spacing, typography, etc.
    value: Any
    category: str | None = None


class FigmaIntegration:
    """
    Figma API integration for Maya Patel's design system management.

    This class provides methods to interact with Figma for retrieving design files,
    exporting assets, synchronizing the design system, and tracking design changes.

    IMPORTANT: This integration is exclusively for Maya Patel (maya_patel bot).
    No other leadership bots have Figma access.

    Attributes:
        token: Figma Personal Access Token
        workspace_id: Figma workspace/team ID
        design_system_file_key: Key for the main design system file

    Example:
        >>> figma = FigmaIntegration(
        ...     token="figd_xxx",
        ...     workspace_id="amt_design_team"
        ... )
        >>> files = figma.get_design_files()
        >>> components = figma.sync_design_system()
    """

    # Only Maya Patel can use Figma
    AUTHORIZED_BOT_ID = "maya_patel"

    def __init__(
        self,
        token: str | None = None,
        workspace_id: str | None = None,
        design_system_file_key: str | None = None,
    ) -> None:
        """
        Initialize Figma integration.

        Args:
            token: Figma Personal Access Token (defaults to FIGMA_TOKEN env var)
            workspace_id: Figma workspace/team ID
            design_system_file_key: Key for main design system file
        """
        self.token = token or os.getenv("FIGMA_TOKEN")
        self.workspace_id = workspace_id or os.getenv("FIGMA_WORKSPACE_ID", "amt_design_system")
        self.design_system_file_key = design_system_file_key or os.getenv("FIGMA_DESIGN_SYSTEM_KEY")

        if not self.token:
            logger.warning("No Figma token provided - operations will fail")

        logger.info(f"FigmaIntegration initialized for workspace: {self.workspace_id}")

    def authenticate(self, bot_id: str) -> bool:
        """
        Authenticate and verify bot has Figma access.

        Args:
            bot_id: Bot ID attempting to access Figma

        Returns:
            True if authenticated and authorized, False otherwise

        Example:
            >>> figma = FigmaIntegration()
            >>> if figma.authenticate("maya_patel"):
            ...     print("Maya has Figma access")
        """
        # Check authorization
        if bot_id != self.AUTHORIZED_BOT_ID:
            logger.error(f"Figma access denied for {bot_id} - Only {self.AUTHORIZED_BOT_ID} has access")
            return False

        if not self.token:
            logger.error("No Figma token available")
            return False

        try:
            import requests

            # Test authentication with Figma API
            headers = {"X-Figma-Token": self.token}
            response = requests.get("https://api.figma.com/v1/me", headers=headers, timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Authenticated to Figma as: {user_data.get('email', 'unknown')}")
                return True
            else:
                logger.error(f"Figma authentication failed: {response.status_code}")
                return False

        except ImportError:
            logger.exception("requests library not installed")
            return False
        except Exception as e:
            logger.exception(f"Figma authentication error: {e}")
            return False

    def get_design_files(self, bot_id: str = "maya_patel") -> list[FigmaFile]:
        """
        Get all design files from the workspace.

        Args:
            bot_id: Bot ID (must be maya_patel)

        Returns:
            List of FigmaFile objects

        Example:
            >>> files = figma.get_design_files()
            >>> for file in files:
            ...     print(f"{file.name}: {file.key}")
        """
        if not self.authenticate(bot_id):
            return []

        if not self.workspace_id:
            logger.error("No workspace ID configured")
            return []

        try:
            import requests

            headers = {"X-Figma-Token": self.token}
            url = f"https://api.figma.com/v1/teams/{self.workspace_id}/projects"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                logger.error(f"Failed to get projects: {response.status_code}")
                return []

            projects = response.json().get("projects", [])
            all_files = []

            # Get files from each project
            for project in projects:
                project_id = project.get("id")
                files_url = f"https://api.figma.com/v1/projects/{project_id}/files"
                files_response = requests.get(files_url, headers=headers, timeout=10)

                if files_response.status_code == 200:
                    files_data = files_response.json().get("files", [])

                    for file_data in files_data:
                        figma_file = FigmaFile(
                            key=file_data.get("key", ""),
                            name=file_data.get("name", "Untitled"),
                            last_modified=datetime.fromisoformat(
                                file_data.get("last_modified", datetime.now(UTC).isoformat()).replace("Z", "+00:00")
                            ),
                            thumbnail_url=file_data.get("thumbnail_url"),
                        )
                        all_files.append(figma_file)

            logger.info(f"Retrieved {len(all_files)} design files from Figma")
            return all_files

        except Exception as e:
            logger.exception(f"Error getting design files: {e}")
            return []

    def export_assets(
        self, file_key: str, node_ids: Sequence[str], format: str = "svg", bot_id: str = "maya_patel"
    ) -> dict[str, str]:
        """
        Export design assets from a Figma file.

        Args:
            file_key: Figma file key
            node_ids: List of node IDs to export
            format: Export format (svg, png, jpg, pdf)
            bot_id: Bot ID (must be maya_patel)

        Returns:
            Dictionary mapping node_id to export URL

        Example:
            >>> exports = figma.export_assets(
            ...     file_key="abc123",
            ...     node_ids=["1:2", "1:3"],
            ...     format="svg"
            ... )
        """
        if not self.authenticate(bot_id):
            return {}

        try:
            import requests

            headers = {"X-Figma-Token": self.token}
            node_ids_str = ",".join(node_ids)

            url = f"https://api.figma.com/v1/images/{file_key}"
            params = {"ids": node_ids_str, "format": format}

            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                images = data.get("images", {})
                logger.info(f"Exported {len(images)} assets from Figma")
                return images
            else:
                logger.error(f"Failed to export assets: {response.status_code}")
                return {}

        except Exception as e:
            logger.exception(f"Error exporting assets: {e}")
            return {}

    def sync_design_system(self, bot_id: str = "maya_patel") -> list[FigmaComponent]:
        """
        Synchronize the design system components from Figma.

        Args:
            bot_id: Bot ID (must be maya_patel)

        Returns:
            List of FigmaComponent objects

        Example:
            >>> components = figma.sync_design_system()
            >>> for component in components:
            ...     print(f"{component.name}: {component.component_id}")
        """
        if not self.authenticate(bot_id):
            return []

        if not self.design_system_file_key:
            logger.error("No design system file key configured")
            return []

        try:
            import requests

            headers = {"X-Figma-Token": self.token}
            url = f"https://api.figma.com/v1/files/{self.design_system_file_key}/components"

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to sync design system: {response.status_code}")
                return []

            data = response.json()
            components_data = data.get("meta", {}).get("components", [])
            components = []

            for comp_data in components_data:
                component = FigmaComponent(
                    component_id=comp_data.get("key", ""),
                    name=comp_data.get("name", "Unnamed"),
                    description=comp_data.get("description"),
                    component_set_id=comp_data.get("component_set_id"),
                    created_at=datetime.fromisoformat(
                        comp_data.get("created_at", datetime.now(UTC).isoformat()).replace("Z", "+00:00")
                    )
                    if comp_data.get("created_at")
                    else None,
                )
                components.append(component)

            logger.info(f"Synced {len(components)} components from design system")
            return components

        except Exception as e:
            logger.exception(f"Error syncing design system: {e}")
            return []

    def extract_design_tokens(self, file_key: str, bot_id: str = "maya_patel") -> list[DesignToken]:
        """
        Extract design tokens from a Figma file.

        This is a simplified implementation. In production, you'd use a
        design token plugin or parser.

        Args:
            file_key: Figma file key
            bot_id: Bot ID (must be maya_patel)

        Returns:
            List of DesignToken objects

        Example:
            >>> tokens = figma.extract_design_tokens("abc123")
            >>> for token in tokens:
            ...     print(f"{token.token_name}: {token.value}")
        """
        if not self.authenticate(bot_id):
            return []

        try:
            import requests

            headers = {"X-Figma-Token": self.token}
            url = f"https://api.figma.com/v1/files/{file_key}"

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to get file: {response.status_code}")
                return []

            # Simplified token extraction
            # In production, use a proper design token parser
            tokens = []

            # Example: Extract colors from styles
            data = response.json()
            styles = data.get("styles", {})

            for style_key, style_data in styles.items():
                if style_data.get("styleType") == "FILL":
                    token = DesignToken(
                        token_name=style_data.get("name", f"color_{style_key}"),
                        token_type="color",
                        value=style_data.get("description", "#000000"),
                        category="colors",
                    )
                    tokens.append(token)

            logger.info(f"Extracted {len(tokens)} design tokens")
            return tokens

        except Exception as e:
            logger.exception(f"Error extracting design tokens: {e}")
            return []

    def track_design_changes(
        self, file_key: str, since_version: str | None = None, bot_id: str = "maya_patel"
    ) -> dict[str, Any]:
        """
        Track changes to a design file.

        Args:
            file_key: Figma file key
            since_version: Version ID to compare from (optional)
            bot_id: Bot ID (must be maya_patel)

        Returns:
            Dictionary with change information

        Example:
            >>> changes = figma.track_design_changes("abc123")
            >>> print(changes['total_changes'])
        """
        if not self.authenticate(bot_id):
            return {"error": "Authentication failed"}

        try:
            import requests

            headers = {"X-Figma-Token": self.token}
            url = f"https://api.figma.com/v1/files/{file_key}/versions"

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to get versions: {response.status_code}")
                return {"error": f"Failed to get versions: {response.status_code}"}

            data = response.json()
            versions = data.get("versions", [])

            # Filter versions since specified version
            if since_version:
                filtered_versions = [
                    v for v in versions if v.get("id", "") > since_version  # Simple string comparison
                ]
            else:
                filtered_versions = versions

            return {
                "file_key": file_key,
                "total_versions": len(versions),
                "new_versions": len(filtered_versions),
                "latest_version": versions[0] if versions else None,
                "changes": filtered_versions[:10],  # Last 10 changes
            }

        except Exception as e:
            logger.exception(f"Error tracking changes: {e}")
            return {"error": str(e)}

    def __repr__(self) -> str:
        """String representation of FigmaIntegration."""
        has_token = bool(self.token)
        return (
            f"FigmaIntegration(workspace='{self.workspace_id}', "
            f"authorized_bot='{self.AUTHORIZED_BOT_ID}', "
            f"authenticated={has_token})"
        )
