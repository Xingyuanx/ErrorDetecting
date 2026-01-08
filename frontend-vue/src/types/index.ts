export interface Cluster {
  uuid: string;
  name: string;
  type: string;
  node_count: number;
  health_status: 'healthy' | 'warning' | 'error' | 'unknown';
  description?: string;
  healthText?: string;
}

export interface Node {
  name: string;
  ip?: string;
  ip_address?: string;
  status: 'healthy' | 'warning' | 'error' | 'running';
  cpu?: string;
  mem?: string;
  updated?: string;
}

export interface ClusterRegisterPayload extends Omit<Cluster, 'uuid' | 'healthText'> {
  namenode_ip?: string;
  namenode_psw?: string;
  rm_ip?: string;
  rm_psw?: string;
  nodes: Array<{
    hostname: string;
    ip_address: string;
    ssh_user: string;
    ssh_password: string;
  }>;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface LogEntry {
  id: string | number;
  time: string;
  level: string;
  source: string;
  message: string;
}
