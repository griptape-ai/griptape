from __future__ import annotations

from typing import Optional, Iterable, Union

import sentence_transformers
import torch
from attr import define, field, Factory

from griptape.drivers import BaseEmbeddingDriver


@define
class SentenceTransformersEmbeddingDriver(BaseEmbeddingDriver):
    """Embedding driver that uses the SentenceTransformers library for generating embeddings locally.

    Attributes:
        model_name_or_path: If it is a filepath on disc, it loads the model from that path. If it is not a path, it
            first tries to download a pre-trained SentenceTransformer model. If that fails, tries to construct a model
            from Huggingface models repository with that name.
        modules: This parameter can be used to create custom SentenceTransformer models from scratch.
        device: Device (like ‘cuda’ / ‘cpu’) that should be used for computation. If None, checks if a GPU can be used.
        cache_folder: Path to store models
        use_auth_token: HuggingFace authentication token to download private models.
        normalize_embeddings: If set to true, returned vectors will have length 1. In that case, the faster dot-product
            (util.dot_score) instead of cosine similarity can be used.
    """

    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    model_name_or_path: Optional[str] = field(default=DEFAULT_MODEL, kw_only=True)
    modules: Optional[Iterable[torch.nn.modules.module.Module]] = field(default=None, kw_only=True)
    device: Optional[str] = field(default=None, kw_only=True)
    cache_folder: Optional[str] = field(default=None, kw_only=True)
    use_auth_token: Optional[Union[bool, str]] = field(default=None, kw_only=True)
    normalize_embeddings: bool = field(default=None, kw_only=True)
    model: sentence_transformers.SentenceTransformer = field(
        default=Factory(
            lambda self: sentence_transformers.SentenceTransformer(
                model_name_or_path=self.model_name_or_path,
                modules=self.modules,
                device=self.device,
                cache_folder=self.cache_folder,
                use_auth_token=self.use_auth_token,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    dimensions: int = field(default=Factory(lambda self: self.model.get_sentence_embedding_dimension(), takes_self=True), kw_only=True)

    def try_embed_string(self, string: str) -> list[float]:
        """Embed a string using the SentenceTransformers library.

        Args:
            string: The string to embed.

        Returns:
            A list of floats representing the embedding.
        """
        return self.model.encode([string], normalize_embeddings=self.normalize_embeddings)[0].tolist()
