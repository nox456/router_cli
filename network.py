"""
Clase Network para gestionar la topología de red y orquestar dispositivos
"""
from device import Device
from data_structures import LinkedList
import json

class NetworkStatistics:
    """Estadísticas globales de la red"""
    
    def __init__(self):
        self.total_packets_sent = 0
        self.total_packets_delivered = 0
        self.total_packets_dropped_ttl = 0
        self.total_packets_dropped_firewall = 0
        self.total_hops = 0
        self.device_activity = {}  # Actividad por dispositivo
    
    def update_packet_sent(self, device_name):
        """Actualiza estadística de paquete enviado"""
        self.total_packets_sent += 1
        self._update_device_activity(device_name)
    
    def update_packet_delivered(self, hops_count):
        """Actualiza estadística de paquete entregado"""
        self.total_packets_delivered += 1
        self.total_hops += hops_count
    
    def update_packet_dropped_ttl(self):
        """Actualiza estadística de paquete descartado por TTL"""
        self.total_packets_dropped_ttl += 1
    
    def update_packet_dropped_firewall(self):
        """Actualiza estadística de paquete bloqueado por firewall"""
        self.total_packets_dropped_firewall += 1
    
    def _update_device_activity(self, device_name):
        """Actualiza la actividad de un dispositivo"""
        if device_name not in self.device_activity:
            self.device_activity[device_name] = 0
        self.device_activity[device_name] += 1
    
    def get_average_hops(self):
        """Calcula el promedio de saltos por paquete entregado"""
        if self.total_packets_delivered == 0:
            return 0
        return round(self.total_hops / self.total_packets_delivered, 1)
    
    def get_top_talker(self):
        """Retorna el dispositivo con más actividad"""
        if not self.device_activity:
            return None
        
        top_device = max(self.device_activity.items(), key=lambda x: x[1])
        return f"{top_device[0]} (processed {top_device[1]} packets)"

class Network:
    """Red que orquesta todos los dispositivos y conexiones"""
    
    def __init__(self):
        self.devices = {}  # Diccionario de dispositivos por nombre
        self.statistics = NetworkStatistics()
        self.current_device = None  # Dispositivo actual en la consola
    
    def add_device(self, name, device_type="router"):
        """Agrega un nuevo dispositivo a la red"""
        if name not in self.devices:
            self.devices[name] = Device(name, device_type)
            return True
        return False
    
    def get_device(self, name):
        """Obtiene un dispositivo por nombre"""
        return self.devices.get(name)
    
    def remove_device(self, name):
        """Remueve un dispositivo de la red"""
        if name in self.devices:
            device = self.devices[name]
            
            # Desconectar todas las interfaces
            for interface in device.interfaces.values():
                connected_list = interface.connected_interfaces.to_list()
                for connected_if in connected_list:
                    interface.disconnect_from(connected_if)
            
            del self.devices[name]
            return True
        return False
    
    def connect_devices(self, device1_name, interface1_name, device2_name, interface2_name):
        """Conecta dos interfaces de dispositivos diferentes"""
        device1 = self.get_device(device1_name)
        device2 = self.get_device(device2_name)
        
        if not device1 or not device2:
            return False
        
        interface1 = device1.get_interface(interface1_name)
        interface2 = device2.get_interface(interface2_name)
        
        if not interface1 or not interface2:
            return False
        
        if not interface1.is_up or not interface2.is_up:
            return False
        
        interface1.connect_to(interface2)
        return True
    
    def disconnect_devices(self, device1_name, interface1_name, device2_name, interface2_name):
        """Desconecta dos interfaces de dispositivos"""
        device1 = self.get_device(device1_name)
        device2 = self.get_device(device2_name)
        
        if not device1 or not device2:
            return False
        
        interface1 = device1.get_interface(interface1_name)
        interface2 = device2.get_interface(interface2_name)
        
        if not interface1 or not interface2:
            return False
        
        interface1.disconnect_from(interface2)
        return True
    
    def set_device_status(self, device_name, status):
        """Cambia el estado online/offline de un dispositivo"""
        device = self.get_device(device_name)
        if not device:
            return False
        
        if status.lower() == "online":
            device.set_online()
            return True
        elif status.lower() == "offline":
            device.set_offline()
            return True
        return False
    
    def list_devices(self):
        """Lista todos los dispositivos en la red"""
        device_list = []
        for device in self.devices.values():
            status = "online" if device.is_online else "offline"
            device_list.append(f"- {device.name} ({status})")
        return device_list
    
    def tick(self):
        """Avanza un paso de simulación procesando todas las colas"""
        tick_results = []
        
        for device in self.devices.values():
            if device.is_online:
                results = device.process_all_interfaces()
                
                # Procesar resultados salientes
                for packet, destination in results['outgoing']:
                    tick_results.append(f"[Tick] {device.name} → {destination}: packet forwarded (TTL={packet.ttl})")
                    
                    if packet.dropped:
                        self.statistics.update_packet_dropped_ttl()
                    else:
                        self.statistics._update_device_activity(device.name)
                
                # Procesar paquetes entregados
                for packet in results['incoming']:
                    if packet.delivered:
                        tick_results.append(f"[Tick] {device.name}: packet delivered from {packet.source_ip}")
                        self.statistics.update_packet_delivered(packet.get_hops_count())
        
        return tick_results
    
    def find_device_by_ip(self, ip_address):
        """Encuentra un dispositivo por su dirección IP"""
        for device in self.devices.values():
            for interface in device.interfaces.values():
                if interface.ip_address == ip_address:
                    return device
        return None
    
    def get_network_statistics(self):
        """Retorna las estadísticas globales de la red"""
        return {
            'total_packets_sent': self.statistics.total_packets_sent,
            'delivered': self.statistics.total_packets_delivered,
            'dropped_ttl': self.statistics.total_packets_dropped_ttl,
            'dropped_firewall': self.statistics.total_packets_dropped_firewall,
            'average_hops': self.statistics.get_average_hops(),
            'top_talker': self.statistics.get_top_talker()
        }
    
    def save_configuration(self, filename="running-config.json"):
        """Guarda la configuración de la red en formato JSON"""
        config = {
            'devices': {name: device.to_dict() for name, device in self.devices.items()},
            'connections': self._get_all_connections(),
            'statistics': self.get_network_statistics()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def _get_all_connections(self):
        """Obtiene todas las conexiones de la red"""
        connections = []
        processed_pairs = set()
        
        for device_name, device in self.devices.items():
            for interface_name, interface in device.interfaces.items():
                for connected_if in interface.connected_interfaces.to_list():
                    pair = tuple(sorted([
                        f"{device_name}:{interface_name}",
                        f"{connected_if.device.name}:{connected_if.name}"
                    ]))
                    
                    if pair not in processed_pairs:
                        connections.append({
                            'device1': device_name,
                            'interface1': interface_name,
                            'device2': connected_if.device.name,
                            'interface2': connected_if.name
                        })
                        processed_pairs.add(pair)
        
        return connections
    
    def load_configuration(self, filename):
        """Carga una configuración desde un archivo JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Limpiar red actual
            self.devices.clear()
            self.statistics = NetworkStatistics()
            
            # Recrear dispositivos
            for device_name, device_data in config.get('devices', {}).items():
                self.add_device(device_name, device_data.get('type', device_data.get('device_type', 'router')))
                device = self.get_device(device_name)
                
                # Configurar interfaces
                for interface_name, interface_data in device_data.get('interfaces', {}).items():
                    device.add_interface(interface_name)
                    interface = device.get_interface(interface_name)
                    
                    if interface_data.get('ip_address'):
                        interface.set_ip_address(interface_data['ip_address'])
                    
                    if interface_data.get('is_up'):
                        interface.no_shutdown()
                    else:
                        interface.shutdown()
                
                # Restaurar estado del dispositivo
                if not device_data.get('online', device_data.get('is_online', True)):
                    device.set_offline()
            
            # Recrear conexiones
            for conn in config.get('connections', []):
                self.connect_devices(
                    conn['device1'], conn['interface1'],
                    conn['device2'], conn['interface2']
                )
            
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False