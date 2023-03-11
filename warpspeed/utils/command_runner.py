import subprocess
from attrs import define


@define
class CommandRunner:
    def run(self, command: str) -> str:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        if len(stderr) == 0:
            return stdout.decode().strip()
        else:
            return f"error: {stderr.decode().strip()}"
