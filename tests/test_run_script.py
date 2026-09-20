from pathlib import Path

import run


def test_verify_installation_handles_failed_command(monkeypatch):
    def fake_run_command(cmd, capture_output=False, check=True):
        return False

    monkeypatch.setattr(run, 'run_command', fake_run_command)

    result = run.verify_installation(Path('venv'))

    assert result is True
