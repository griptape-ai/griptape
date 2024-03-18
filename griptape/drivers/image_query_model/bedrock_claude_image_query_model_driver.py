from __future__ import annotations

import base64
from typing import Any, Optional

from attr import field, define

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryModelDriver


@define
class BedrockClaudeImageQueryModelDriver(BaseImageQueryModelDriver):

    def query_image_request_parameters(self) -> dict:
        return {}
    
    def process_output(self, output: Any) -> TextArtifact:
        return  TextArtifact("")