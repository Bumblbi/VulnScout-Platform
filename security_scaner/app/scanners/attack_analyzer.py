import networkx as nx
from typing import Dict, List
from app.models.vulnerability_models import SeverityLevel

class AttackAnalyzer:
    def __init__(self):
        self.attack_graph = nx.DiGraph()
        self.attack_patterns = self._load_attack_patterns()
    
    def _load_attack_patterns(self) -> List[Dict]:
        """Загрузка шаблонов атак"""
        return [
            {
                'name': 'WebApp_to_RCE',
                'pattern': [
                    {'type': 'web_vulnerability', 'severity': ['high', 'critical']},
                    {'type': 'command_injection', 'severity': ['critical']}
                ],
                'description': 'Web уязвимость приводит к выполнению команд'
            },
            {
                'name': 'Credential_BruteForce_to_Access',
                'pattern': [
                    {'type': 'bruteforce_success', 'severity': any},
                    {'type': 'service_access', 'severity': any}
                ],
                'description': 'Успешный подбор учетных данных приводит к доступу'
            }
        ]
    
    def build_attack_vectors(self, scan_results: Dict) -> List[Dict]:
        """Построение цепочек атак на основе результатов сканирования"""
        vectors = []
        
        network_data = scan_results.get('network', {})
        vulnerabilities = scan_results.get('vulnerabilities', [])
        attacks = scan_results.get('attacks', {})
        
        # Строим граф атаки
        self._build_attack_graph(network_data, vulnerabilities, attacks)
        
        # Находим пути атаки
        attack_paths = self._find_attack_paths()
        
        # Преобразуем в формат для БД
        for path in attack_paths:
            if len(path) >= 2:
                vector = {
                    'source': path[0]['description'],
                    'target': path[-1]['description'],
                    'description': self._generate_vector_description(path),
                    'confidence': self._calculate_path_confidence(path)
                }
                vectors.append(vector)
        
        return vectors
    
    def _build_attack_graph(self, network_data: Dict, vulnerabilities: List[Dict], attacks: Dict):
        """Построение графа атаки"""
        self.attack_graph.clear()
        
        # Добавляем узлы для хостов
        for host in network_data.get('hosts', []):
            host_node = f"host_{host['ip']}"
            self.attack_graph.add_node(host_node, type='host', data=host)
        
        # Добавляем узлы для уязвимостей
        for vuln in vulnerabilities:
            vuln_node = f"vuln_{vuln.get('host')}_{hash(str(vuln))}"
            self.attack_graph.add_node(vuln_node, type='vulnerability', data=vuln)
            
            # Связываем уязвимость с хостом
            host_node = f"host_{vuln.get('host')}"
            if host_node in self.attack_graph:
                self.attack_graph.add_edge(host_node, vuln_node, weight=0.5)
        
        # Добавляем узлы для успешных атак
        for host_ip, host_attacks in attacks.items():
            for attack_type, result in host_attacks.items():
                if result.get('success'):
                    attack_node = f"attack_{host_ip}_{attack_type}"
                    self.attack_graph.add_node(attack_node, type='attack', data=result)
                    
                    # Связываем атаку с хостом
                    host_node = f"host_{host_ip}"
                    if host_node in self.attack_graph:
                        self.attack_graph.add_edge(attack_node, host_node, weight=0.8)
        
        # Связываем связанные уязвимости
        self._connect_related_vulnerabilities()
    
    def _connect_related_vulnerabilities(self):
        """Связывание связанных уязвимостей"""
        vuln_nodes = [n for n, attr in self.attack_graph.nodes(data=True) if attr.get('type') == 'vulnerability']
        
        for i, vuln1 in enumerate(vuln_nodes):
            for vuln2 in vuln_nodes[i+1:]:
                data1 = self.attack_graph.nodes[vuln1]['data']
                data2 = self.attack_graph.nodes[vuln2]['data']
                
                if self._are_vulnerabilities_related(data1, data2):
                    self.attack_graph.add_edge(vuln1, vuln2, weight=0.6)
    
    def _are_vulnerabilities_related(self, vuln1: Dict, vuln2: Dict) -> bool:
        """Проверка связанности уязвимостей"""
        # Уязвимости на одном хосте
        if vuln1.get('host') == vuln2.get('host'):
            return True
        
        # Уязвимости одного типа
        if vuln1.get('vulnerability', {}).get('cve', {}).get('id') == vuln2.get('vulnerability', {}).get('cve', {}).get('id'):
            return True
        
        return False
    
    def _find_attack_paths(self) -> List[List[Dict]]:
        """Поиск путей атаки в графе"""
        paths = []
        
        # Находим начальные точки атаки (внешние хосты с уязвимостями)
        start_nodes = [
            n for n, attr in self.attack_graph.nodes(data=True) 
            if attr.get('type') in ['attack', 'vulnerability'] 
            and self._is_external_node(n)
        ]
        
        # Находим целевые точки (критические уязвимости)
        target_nodes = [
            n for n, attr in self.attack_graph.nodes(data=True)
            if attr.get('type') == 'vulnerability'
            and self._is_critical_vulnerability(attr.get('data', {}))
        ]
        
        # Ищем пути от начальных к целевым точкам
        for start in start_nodes:
            for target in target_nodes:
                try:
                    path = nx.shortest_path(self.attack_graph, start, target)
                    path_data = [self.attack_graph.nodes[node] for node in path]
                    paths.append(path_data)
                except nx.NetworkXNoPath:
                    continue
        
        return paths
    
    def _is_external_node(self, node: str) -> bool:
        """Проверка, является ли узел внешней точкой входа"""
        # Простая эвристика - все хосты считаются внешними
        return True
    
    def _is_critical_vulnerability(self, vuln_data: Dict) -> bool:
        """Проверка, является ли уязвимость критической"""
        severity = vuln_data.get('severity')
        if isinstance(severity, SeverityLevel):
            return severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
        elif isinstance(severity, str):
            return severity in ['critical', 'high']
        return False
    
    def _generate_vector_description(self, path: List[Dict]) -> str:
        """Генерация описания для вектора атаки"""
        if len(path) < 2:
            return "Short attack vector"
        
        steps = []
        for node in path:
            node_type = node.get('type')
            node_data = node.get('data', {})
            
            if node_type == 'attack':
                steps.append(f"Successful {list(node_data.keys())[0]} attack")
            elif node_type == 'vulnerability':
                vuln_title = node_data.get('title', 'Unknown vulnerability')
                steps.append(f"Exploit {vuln_title}")
            elif node_type == 'host':
                steps.append(f"Access to {node_data.get('ip', 'unknown host')}")
        
        return " → ".join(steps)
    
    def _calculate_path_confidence(self, path: List[Dict]) -> float:
        """Расчет уверенности в векторе атаки"""
        if not path:
            return 0.0
        
        total_weight = 0.0
        edge_count = 0
        
        # Преобразуем путь обратно в узлы графа
        node_names = []
        for node_data in path:
            # Находим имя узла по данным (упрощенная логика)
            for node_name, attr in self.attack_graph.nodes(data=True):
                if attr.get('data') == node_data.get('data'):
                    node_names.append(node_name)
                    break
        
        # Рассчитываем вес пути
        for i in range(len(node_names) - 1):
            edge_data = self.attack_graph.get_edge_data(node_names[i], node_names[i + 1])
            if edge_data:
                total_weight += edge_data.get('weight', 0.5)
                edge_count += 1
        
        if edge_count == 0:
            return 0.5  # Средняя уверенность по умолчанию
        
        return total_weight / edge_count
    
    def get_attack_graph_visualization(self) -> Dict:
        """Получение данных для визуализации графа атаки"""
        nodes = []
        edges = []
        
        for node, attr in self.attack_graph.nodes(data=True):
            nodes.append({
                'id': node,
                'type': attr.get('type', 'unknown'),
                'label': self._get_node_label(attr),
                'data': attr.get('data', {})
            })
        
        for edge in self.attack_graph.edges(data=True):
            edges.append({
                'source': edge[0],
                'target': edge[1],
                'weight': edge[2].get('weight', 0.5)
            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def _get_node_label(self, node_attr: Dict) -> str:
        """Генерация метки для узла"""
        node_type = node_attr.get('type')
        data = node_attr.get('data', {})
        
        if node_type == 'host':
            return data.get('ip', 'Unknown host')
        elif node_type == 'vulnerability':
            return data.get('title', 'Unknown vulnerability')[:30]
        elif node_type == 'attack':
            attack_type = list(data.keys())[0] if data else 'attack'
            return f"Successful {attack_type}"
        
        return 'Unknown'