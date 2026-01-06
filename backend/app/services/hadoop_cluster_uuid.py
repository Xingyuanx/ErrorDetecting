from __future__ import annotations

from ..config import SSH_TIMEOUT
from ..ssh_utils import SSHClient


def collect_cluster_uuid(host: str, user: str, password: str, timeout: int | None = None) -> tuple[str | None, str | None, str | None]:
    cli = None
    try:
        cli = SSHClient(str(host), user or "", password or "")
        out, err = cli.execute_command_with_timeout(
            "hdfs getconf -confKey dfs.namenode.name.dir",
            timeout or SSH_TIMEOUT,
        )
        if not out or not out.strip():
            return None, "probe_name_dirs", (err or "empty_output")

        name_dir = out.strip().split(",")[0]
        if name_dir.startswith("file://"):
            name_dir = name_dir[7:]
        version_path = f"{name_dir.rstrip('/')}/current/VERSION"

        version_out, version_err = cli.execute_command_with_timeout(
            f"cat {version_path}",
            timeout or SSH_TIMEOUT,
        )
        if not version_out or not version_out.strip():
            return None, "read_version", (version_err or "empty_output")

        cluster_id = None
        for line in version_out.splitlines():
            if "clusterID" in line:
                parts = line.strip().split("=", 1)
                if len(parts) == 2 and parts[0].strip() == "clusterID":
                    cluster_id = parts[1].strip()
                    break
        if not cluster_id:
            return None, "parse_cluster_id", version_out.strip()

        if cluster_id.startswith("CID-"):
            cluster_id = cluster_id[4:]
        return cluster_id, None, None
    except Exception as e:
        return None, "connect_or_exec", str(e)
    finally:
        try:
            if cli:
                cli.close()
        except Exception:
            pass

