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

def get_hdfs_cluster_id(host: str, user: str, password: str, timeout: int | None = None) -> tuple[str | None, str | None]:
    """
    通过以下步骤获取 HDFS 集群 UUID:
    1. 执行 hdfs getconf -confKey dfs.namenode.name.dir 获取名称节点目录。
    2. 在该目录的 current 子目录下读取 VERSION 文件。
    3. 解析 VERSION 文件中的 clusterID 字段。
    4. 去掉 'CID-' 前缀并返回。
    """
    try:
        cli = SSHClient(str(host), user or "", password or "")
        
        # 1. 获取 dfs.namenode.name.dir
        dir_out, dir_err = cli.execute_command_with_timeout("hdfs getconf -confKey dfs.namenode.name.dir", timeout or SSH_TIMEOUT)
        if not dir_out or not dir_out.strip():
            cli.close()
            return None, f"Failed to get dfs.namenode.name.dir: {dir_err or 'Empty output'}"
        
        # 处理可能存在的多个目录（取第一个）
        name_dir = dir_out.strip().split(',')[0]
        # 移除 file:// 前缀（如果存在）
        if name_dir.startswith("file://"):
            name_dir = name_dir[7:]
            
        version_path = f"{name_dir.rstrip('/')}/current/VERSION"
        
        # 2. 读取 VERSION 文件
        version_out, version_err = cli.execute_command_with_timeout(f"cat {version_path}", timeout or SSH_TIMEOUT)
        cli.close()
        
        if not version_out or not version_out.strip():
            return None, f"Failed to read VERSION file at {version_path}: {version_err or 'Empty output'}"
        
        # 3. 解析 clusterID
        cluster_id = None
        for line in version_out.splitlines():
            if line.startswith("clusterID="):
                cluster_id = line.split("=")[1].strip()
                break
        
        if not cluster_id:
            return None, f"clusterID not found in {version_path}"
        
        # 4. 去掉 'CID-' 前缀
        if cluster_id.startswith("CID-"):
            cluster_id = cluster_id[4:]
            
        return cluster_id, None
        
    except Exception as e:
        return None, str(e)
