"""
Clases Device e Interface para simular dispositivos de red
"""
from data_structures import LinkedList, Queue, Stack, AVLTree, BTree, Trie, ErrorLog
from packet import Packet
import re

class Interface:
    """Interfaz de red de un dispositivo"""
    
    def __init__(self, name, device):
        """
        Inicializa una nueva interfaz
        
        Args:
            name (str): Nombre de la interfaz (ej: g0/0, eth0)
            device (Device): Dispositivo al que pertenece la interfaz
        """
        self.name = name
        self.device = device
        self.ip_address = None
        self.is_up = False  # Estado shutdown por defecto
        self.connected_interfaces = LinkedList()  # Vecinos conectados
        self.outgoing_queue = Queue()  # Cola de paquetes salientes
        self.incoming_queue = Queue()  # Cola de paquetes entrantes
    
    def set_ip_address(self, ip):
        """Asigna dirección IP a la interfaz con validación"""
        if self._validate_ip(ip):
            self.ip_address = ip
            return True
        return False
    
    def _validate_ip(self, ip):
        """Valida formato de dirección IP"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        parts = ip.split('.')
        for part in parts:
            if not (0 <= int(part) <= 255):
                return False
        return True
    
    def shutdown(self):
        """Desactiva la interfaz"""
        self.is_up = False
    
    def no_shutdown(self):
        """Activa la interfaz"""
        self.is_up = True
    
    def connect_to(self, other_interface):
        """Conecta esta interfaz con otra interfaz"""
        if other_interface not in self.connected_interfaces.to_list():
            self.connected_interfaces.append(other_interface)
            other_interface.connected_interfaces.append(self)
    
    def disconnect_from(self, other_interface):
        """Desconecta esta interfaz de otra interfaz"""
        self.connected_interfaces.remove(other_interface)
        other_interface.connected_interfaces.remove(self)
    
    def send_packet(self, packet):
        """Envía un paquete a través de esta interfaz"""
        if self.is_up and self.device.is_online:
            self.outgoing_queue.enqueue(packet)
            return True
        return False
    
    def receive_packet(self, packet):
        """Recibe un paquete en esta interfaz"""
        if self.is_up and self.device.is_online:
            self.incoming_queue.enqueue(packet)
            return True
        return False
    
    def process_outgoing_packets(self):
        """Procesa paquetes en la cola de salida"""
        processed_packets = []
        
        while not self.outgoing_queue.is_empty():
            packet = self.outgoing_queue.dequeue()
            if packet and packet.decrement_ttl():
                packet.add_hop(self.device.name)
                
                # Enviar a todas las interfaces conectadas (broadcast para switches)
                packet_sent = False
                for connected_if in self.connected_interfaces.to_list():
                    if connected_if.is_up and connected_if.device.is_online:
                        if connected_if.receive_packet(packet):
                            processed_packets.append((packet, connected_if.device.name))
                            packet_sent = True
                            # Para switches y hubs, enviar a todas las interfaces
                            if self.device.device_type in ["switch", "hub"]:
                                continue
                            else:
                                break  # Para routers, enviar solo a una interfaz
                
                if not packet_sent:
                    packet.mark_dropped("No active next hop")
        
        return processed_packets
    
    def process_incoming_packets(self):
        """Procesa paquetes en la cola de entrada"""
        processed_packets = []
        
        while not self.incoming_queue.is_empty():
            packet = self.incoming_queue.dequeue()
            if packet:
                # Si el paquete es para este dispositivo (tiene IP y coincide)
                if self.ip_address and packet.destination_ip == self.ip_address:
                    packet.mark_delivered()
                    self.device.message_history.push(packet)
                    processed_packets.append(packet)
                else:
                    # Para switches sin IP, o paquetes que no son para este dispositivo, reenviar
                    # Pasar la interfaz de entrada para evitar bucles
                    self.device.forward_packet_from_interface(packet, self)
        
        return processed_packets
    
    def get_status(self):
        """Retorna el estado de la interfaz"""
        return {
            'name': self.name,
            'ip_address': self.ip_address,
            'is_up': self.is_up,
            'connected_to': [iface.device.name + ':' + iface.name 
                           for iface in self.connected_interfaces.to_list()],
            'outgoing_queue_size': len(self.outgoing_queue),
            'incoming_queue_size': len(self.incoming_queue)
        }

class Device:
    """Dispositivo de red (router, switch, host, firewall)"""
    
    def __init__(self, name, device_type="router"):
        """
        Inicializa un nuevo dispositivo
        
        Args:
            name (str): Nombre del dispositivo
            device_type (str): Tipo de dispositivo (router, switch, host, firewall)
        """
        self.name = name
        self.device_type = device_type.lower()
        self.is_online = True
        self.interfaces = {}  # Diccionario de interfaces por nombre
        self.message_history = Stack()  # Historial de mensajes recibidos
        self.packets_sent = 0
        self.packets_received = 0
        self.packets_forwarded = 0
        
        # Módulo 1: Tabla de rutas AVL
        self.routing_table = AVLTree()
        
        # Módulo 2: Índice B-tree para snapshots
        self.snapshot_index = BTree()
        
        # Módulo 3: Trie para prefijos y políticas
        self.prefix_trie = Trie()
        
        # Módulo 4: Log de errores
        self.error_log = ErrorLog()
    
    def add_interface(self, interface_name):
        """Agrega una nueva interfaz al dispositivo"""
        if interface_name not in self.interfaces:
            self.interfaces[interface_name] = Interface(interface_name, self)
            return True
        return False
    
    def get_interface(self, interface_name):
        """Obtiene una interfaz por nombre"""
        return self.interfaces.get(interface_name)
    
    def set_online(self):
        """Pone el dispositivo en línea"""
        self.is_online = True
    
    def set_offline(self):
        """Pone el dispositivo fuera de línea"""
        self.is_online = False
    
    def send_packet(self, source_ip, destination_ip, content, ttl=64):
        """Envía un paquete desde este dispositivo"""
        if not self.is_online:
            return False
        
        # Buscar interfaz con la IP de origen
        source_interface = None
        for interface in self.interfaces.values():
            if interface.ip_address == source_ip:
                source_interface = interface
                break
        
        if not source_interface:
            return False
        
        packet = Packet(source_ip, destination_ip, content, ttl)
        packet.add_hop(self.name)
        
        if source_interface.send_packet(packet):
            self.packets_sent += 1
            return True
        return False
    
    def forward_packet(self, packet):
        """Reenvía un paquete a través del dispositivo"""
        return self.forward_packet_from_interface(packet, None)
    
    def forward_packet_from_interface(self, packet, source_interface):
        """Reenvía un paquete evitando la interfaz de origen con nueva lógica de rutas"""
        if not self.is_online:
            return False
        
        # Verificar políticas en el trie primero (Módulo 3)
        policies = self.prefix_trie.get_inherited_policies(packet.destination_ip)
        
        # Aplicar política de bloqueo
        if 'block' in policies:
            packet.mark_dropped("Blocked by policy")
            self.error_log.log_error("PolicyBlock", f"Packet blocked by policy for {packet.destination_ip}")
            return False
        
        # Aplicar política de TTL mínimo
        if 'ttl-min' in policies and packet.ttl < policies['ttl-min']:
            packet.mark_dropped("TTL below minimum")
            self.error_log.log_error("PolicyTTL", f"TTL {packet.ttl} below minimum {policies['ttl-min']}")
            return False
        
        if self.device_type == "switch":
            # Switch: enviar por todas las interfaces excepto la de entrada
            packet_forwarded = False
            for interface in self.interfaces.values():
                if interface != source_interface and interface.is_up and not interface.connected_interfaces.is_empty():
                    if interface.send_packet(packet):
                        packet_forwarded = True
            
            if packet_forwarded:
                self.packets_forwarded += 1
                return True
        else:
            # Router: usar tabla AVL para routing (Módulo 1)
            route = self.routing_table.lookup(packet.destination_ip)
            if route:
                # Buscar interfaz conectada al next_hop
                for interface in self.interfaces.values():
                    if interface != source_interface and interface.is_up:
                        # Verificar si algún vecino tiene el next_hop
                        for connected_if in interface.connected_interfaces.to_list():
                            if connected_if.ip_address == route.next_hop:
                                if interface.send_packet(packet):
                                    self.packets_forwarded += 1
                                    return True
            
            # Si no hay ruta específica, usar comportamiento original
            for interface in self.interfaces.values():
                if interface != source_interface and interface.is_up and not interface.connected_interfaces.is_empty():
                    if interface.send_packet(packet):
                        self.packets_forwarded += 1
                        return True
        
        # Si no se puede reenviar, descartar
        packet.mark_dropped("No route to destination")
        self.error_log.log_error("RoutingError", f"No route to {packet.destination_ip}")
        return False
    
    def process_all_interfaces(self):
        """Procesa todas las colas de todas las interfaces"""
        results = {
            'outgoing': [],
            'incoming': []
        }
        
        if not self.is_online:
            return results
        
        for interface in self.interfaces.values():
            if interface.is_up:
                outgoing = interface.process_outgoing_packets()
                incoming = interface.process_incoming_packets()
                
                results['outgoing'].extend(outgoing)
                results['incoming'].extend(incoming)
                
                # Actualizar estadísticas
                self.packets_received += len(incoming)
        
        return results
    
    def get_message_history(self):
        """Retorna el historial de mensajes como lista"""
        return self.message_history.to_list()
    
    def get_queue_status(self):
        """Retorna el estado de todas las colas del dispositivo"""
        status = {}
        for name, interface in self.interfaces.items():
            status[name] = {
                'outgoing': interface.outgoing_queue.to_list(),
                'incoming': interface.incoming_queue.to_list()
            }
        return status
    
    def get_interfaces_status(self):
        """Retorna el estado de todas las interfaces"""
        return {name: interface.get_status() 
                for name, interface in self.interfaces.items()}
    
    def to_dict(self):
        """Convierte el dispositivo a diccionario para serialización"""
        return {
            'name': self.name,
            'device_type': self.device_type,
            'is_online': self.is_online,
            'interfaces': {name: {
                'name': iface.name,
                'ip_address': iface.ip_address,
                'is_up': iface.is_up
            } for name, iface in self.interfaces.items()},
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'packets_forwarded': self.packets_forwarded
        }
    
    def save_snapshot(self, key):
        """Guarda un snapshot de la configuración (Módulo 2)"""
        import json
        import os
        from datetime import datetime
        
        # Generar nombre de archivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snap_{timestamp}.cfg"
        filepath = os.path.join("configs", filename)
        
        # Crear directorio si no existe
        os.makedirs("configs", exist_ok=True)
        
        # Preparar datos del snapshot
        snapshot_data = {
            'device_name': self.name,
            'timestamp': datetime.now().isoformat(),
            'routing_table': [],
            'prefix_policies': [],
            'device_config': self.to_dict()
        }
        
        # Exportar rutas del AVL
        for route in self.routing_table.in_order_traversal():
            snapshot_data['routing_table'].append({
                'prefix': route.prefix,
                'mask': route.mask,
                'next_hop': route.next_hop,
                'metric': route.metric
            })
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
            
            # Indexar en el B-tree
            self.snapshot_index.insert(key, filename)
            return True, filename
        except Exception as e:
            self.error_log.log_error("SaveError", f"Failed to save snapshot: {str(e)}")
            return False, str(e)
    
    def load_snapshot(self, key):
        """Carga un snapshot desde el índice B-tree (Módulo 2)"""
        filename = self.snapshot_index.search(key)
        if not filename:
            self.error_log.log_error("LoadError", f"Snapshot key '{key}' not found")
            return False, f"Snapshot key '{key}' not found"
        
        import json
        import os
        
        filepath = os.path.join("configs", filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
            
            # Restaurar tabla de rutas
            self.routing_table = AVLTree()
            for route_data in snapshot_data.get('routing_table', []):
                self.routing_table.insert(
                    route_data['prefix'],
                    route_data['mask'],
                    route_data['next_hop'],
                    route_data['metric']
                )
            
            return True, f"Snapshot loaded from {filename}"
        except Exception as e:
            self.error_log.log_error("LoadError", f"Failed to load snapshot: {str(e)}")
            return False, str(e)