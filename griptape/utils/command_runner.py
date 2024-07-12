import subprocess

from attrs import define

from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact


@define
class CommandRunner:
    def run(self, command: str) -> BaseArtifact:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

        if len(stderr) == 0:
            return TextArtifact(stdout.strip().decode())
        else:
            return ErrorArtifact(f"error: {stderr.strip()}")
