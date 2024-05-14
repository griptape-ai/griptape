from __future__ import annotations

import os
from abc import ABC

from attr import field, define

from griptape.artifacts import MediaArtifact
from griptape.loaders import ImageLoader
from griptape.mixins import RuleMixin, BlobArtifactFileOutputMixin
from griptape.rules import Ruleset, Rule
from griptape.tasks import BaseTask


@define
class BaseAudioGenerationTask(BlobArtifactFileOutputMixin, RuleMixin, BaseTask, ABC):
    ...
