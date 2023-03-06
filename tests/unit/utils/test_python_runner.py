from warpspeed.utils import PythonRunner


class TestPythonRunner:
    def test_run(self):
        assert PythonRunner(libs={"math": "math"}).run("""math.sqrt(9)""") == "3.0"
        assert PythonRunner(libs={"numpy": "np"}).run("""np.array([1, 2, 3])""") == "[1 2 3]"

    def test_run_fail(self):
        assert PythonRunner().run("""np.array([1, 2, 3])""") == "name 'np' is not defined"
