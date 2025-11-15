import nmap
from typing import Dict

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
    
    def scan_target(self, target: str) -> Dict:
        print(f"Starting network scan for {target}")
        
        scan_result = self.nm.scan(
            hosts=target,
            arguments='-sS -T4 --top-ports 1000 -O --version-all'
        )
        
        hosts_data = []
        for host in self.nm.all_hosts():
            host_info = {
                'ip': host,
                'hostname': self.nm[host].hostname(),
                'status': self.nm[host].state(),
                'os': self.nm[host].get('osmatch', []),
                'ports': []
            }
            
            for proto in self.nm[host].all_protocols():
                ports = self.nm[host][proto].keys()
                for port in ports:
                    port_data = self.nm[host][proto][port]
                    host_info['ports'].append({
                        'port': port,
                        'protocol': proto,
                        'state': port_data['state'],
                        'service': port_data.get('name', 'unknown'),
                        'version': port_data.get('version', 'unknown')
                    })
            
            hosts_data.append(host_info)
        
        return {'hosts': hosts_data}