import subprocess
import sys
import language_tutor


def test_cli_version():
    result = subprocess.run(
        [sys.executable, '-m', 'language_tutor.cli', '--version'],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    expected = f"Language Tutor v{language_tutor.__version__}"
    assert expected in result.stdout.strip()
