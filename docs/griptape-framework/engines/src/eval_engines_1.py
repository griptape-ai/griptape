import json

from griptape.engines import EvalEngine

engine = EvalEngine(
    criteria="Determine whether the actual output is factually correct based on the expected output.",
)

score, reason = engine.evaluate(
    input="If you have a red house made of red bricks, a blue house made of blue bricks, what is a greenhouse made of?",
    expected_output="Glass",
    actual_output="Glass",
)

print("Eval Steps", json.dumps(engine.evaluation_steps, indent=2))
print(f"Score: {score}")
print(f"Reason: {reason}")
