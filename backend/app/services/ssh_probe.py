from ..ssh_utils import SSHClient
from ..config import SSH_TIMEOUT

def check_ssh_connectivity(host: str, user: str, password: str, timeout: int | None = None) -> tuple[bool, str | None]:
    try:
        cli = SSHClient(str(host), user or "", password or "")
        out, _ = cli.execute_command_with_timeout("echo ok", timeout or SSH_TIMEOUT)
        cli.close()
        if out is None:
            return (False, "no_output")
        if out.strip():
            return (True, None)
        return (False, "empty_output")
    except Exception as e:
        try:
            cli.close()
        except Exception:
            pass
        return (False, str(e))
