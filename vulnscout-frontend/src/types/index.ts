export interface ScanTask {
  id: string;
  target: string;
  mode: 'black' | 'gray' | 'white';
  intensity: 'low' | 'medium' | 'high';
  status: 'pending' | 'running' | 'completed' | 'error';
  progress: number;
  createdAt: string;
  completedAt?: string;
}

export interface Vulnerability {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  cvssScore: number;
  recommendation: string;
  proof: string;
  port?: number;
  host?: string;
}

export interface ScanResult {
  id: string;
  taskId: string;
  hosts: Host[];
  ports: Port[];
  vulnerabilities: Vulnerability[];
}

export interface Host {
  ip: string;
  hostname?: string;
  os?: string;
}

export interface Port {
  number: number;
  protocol: string;
  service: string;
  state: string;
}