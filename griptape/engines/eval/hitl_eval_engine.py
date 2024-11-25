from __future__ import annotations

from attrs import define

from griptape.engines.eval.eval_engine import EvalEngine
from griptape.mixins.serializable_mixin import SerializableMixin


@define(kw_only=True)
class HitlEvalEngine(EvalEngine, SerializableMixin):
    def evaluate(self, **kwargs) -> tuple[float, str]:
        input_text = (
            "Evaluation Steps: "
            + "\n".join(self.evaluation_steps or [])
            + "\n\nInput: "
            + kwargs["input"].value
            + "\n\nActual Output: "
            + kwargs["actual_output"].value
            + "\n\nReply score,reason: "
        )
        result = input(input_text).split(",", 1)
        return float(result[0]), result[1]
