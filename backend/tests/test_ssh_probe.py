import pytest
from app.services.ssh_probe import check_ssh_connectivity
from app.ssh_utils import SSHClient

class _DummyCli:
    def __init__(self, host, user, pwd):
        self.closed = False
    def execute_command_with_timeout(self, cmd, timeout):
        return ("ok", "")
    def close(self):
        self.closed = True

def test_check_ssh_connectivity_success(monkeypatch):
    monkeypatch.setattr("app.services.ssh_probe.SSHClient", lambda h,u,p: _DummyCli(h,u,p))
    ok, err = check_ssh_connectivity("127.0.0.1", "u", "p", timeout=1)
    assert ok is True
    assert err is None

class _FailCli:
    def __init__(self, host, user, pwd):
        raise RuntimeError("connect_failed")

def test_check_ssh_connectivity_fail(monkeypatch):
    monkeypatch.setattr("app.services.ssh_probe.SSHClient", lambda h,u,p: _FailCli(h,u,p))
    ok, err = check_ssh_connectivity("127.0.0.1", "u", "p", timeout=1)
    assert ok is False
    assert "connect_failed" in str(err)
