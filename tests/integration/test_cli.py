import os
import subprocess
import sys
import tempfile

import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALL_VALUES = os.path.join(PROJECT_DIR, "all-values.yaml")
CT600_PDF = os.path.join(PROJECT_DIR, "CT600.pdf")
SPEC_JSON = os.path.join(PROJECT_DIR, "spec.json")


@pytest.fixture
def output_pdf(tmp_path):
    return str(tmp_path / "output.pdf")


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "ct600_fill"] + list(args),
        capture_output=True,
        cwd=PROJECT_DIR,
    )


class TestCLIEndToEnd:
    def test_produces_output_pdf(self, output_pdf):
        result = run_cli(
            "--input", ALL_VALUES,
            "--output", output_pdf,
            "--ct600", CT600_PDF,
            "--spec", SPEC_JSON,
        )
        assert result.returncode == 0, f"stderr: {result.stderr.decode()}"
        assert os.path.exists(output_pdf)
        with open(output_pdf, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_output_pdf_has_nonzero_size(self, output_pdf):
        result = run_cli(
            "--input", ALL_VALUES,
            "--output", output_pdf,
            "--ct600", CT600_PDF,
            "--spec", SPEC_JSON,
        )
        assert result.returncode == 0
        assert os.path.getsize(output_pdf) > 0

    def test_help_flag(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert b"usage" in result.stdout.lower() or b"Usage" in result.stdout

    def test_missing_input_file_errors(self, output_pdf):
        result = run_cli(
            "--input", "/nonexistent/file.yaml",
            "--output", output_pdf,
            "--ct600", CT600_PDF,
            "--spec", SPEC_JSON,
        )
        assert result.returncode != 0
