"""Isolated course export service used to demonstrate a CodeQL finding.

This module is not imported by Mini-LMS and must never be deployed. It models an
internal staff tool while preserving an intentional command-injection data flow.
"""

import subprocess

from fastapi import FastAPI


course_tools_app = FastAPI()


@course_tools_app.post("/staff/tools/export-course")
def export_course(course_slug: str, output_file: str) -> dict[str, str | int]:
    """Export course materials to an archive selected by a staff member."""
    command = (
        "python scripts/export_course.py "
        f"--course {course_slug} --output {output_file}"
    )
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    return {
        "archive": output_file,
        "exit_code": completed.returncode,
        "details": completed.stdout,
    }
