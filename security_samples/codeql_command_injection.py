"""Intentionally vulnerable CodeQL canary.

This module is not imported by Mini-LMS and must never be deployed or connected
to the production application. It exists only to demonstrate that CodeQL finds
the py/command-line-injection data flow in a pull request. Remove it after the
classroom demonstration.
"""

import subprocess

from fastapi import FastAPI


demo_app = FastAPI()


@demo_app.get("/codeql-demo/run")
def run_untrusted_command(command: str) -> dict[str, str]:
    """Deliberately pass remote input to a shell for the CodeQL demonstration."""
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    return {"output": completed.stdout}
