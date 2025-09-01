"""
Gestor de configuración para guardar y cargar estado del simulador
"""
import json
import os
from datetime import datetime

class ConfigurationManager:
    """Maneja la persistencia de configuración del simulador"""
    
    def __init__(self, network):
        self.network = network
        self.config_dir = "configs"
        self._ensure_config_directory()
    
    def _ensure_config_directory(self):
        """Crea el directorio de configuraciones si no existe"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def save_running_config(self, filename=None):
        """
        Guarda la configuración actual en formato JSON
        
        Args:
            filename (str): Nombre del archivo, por defecto running-config.json
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"running-config_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(self.config_dir, filename)
        
        config_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Router Simulator Configuration"
            },
            "devices": {},
            "connections": [],
            "statistics": self.network.get_network_statistics()
        }
        
        # Serializar dispositivos
        for device_name, device in self.network.devices.items():
            config_data["devices"][device_name] = {
                "name": device.name,
                "type": device.device_type,
                "online": device.is_online,
                "interfaces": {}
            }
            
            # Serializar interfaces
            for interface_name, interface in device.interfaces.items():
                config_data["devices"][device_name]["interfaces"][interface_name] = {
                    "name": interface.name,
                    "ip_address": interface.ip_address,
                    "is_up": interface.is_up,
                    "outgoing_queue_size": len(interface.outgoing_queue),
                    "incoming_queue_size": len(interface.incoming_queue)
                }
        
        # Serializar conexiones
        config_data["connections"] = self._get_network_connections()
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True, f"Configuration saved to {filepath}"
            
        except Exception as e:
            return False, f"Error saving configuration: {str(e)}"
    
    def load_config(self, filename):
        """
        Carga una configuración desde un archivo JSON
        
        Args:
            filename (str): Nombre del archivo de configuración
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(self.config_dir, filename)
        
        if not os.path.exists(filepath):
            return False, f"Configuration file {filepath} not found"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validar estructura del archivo
            if not self._validate_config_structure(config_data):
                return False, "Invalid configuration file structure"
            
            # Limpiar red actual
            self.network.devices.clear()
            
            # Recrear dispositivos
            for device_name, device_config in config_data["devices"].items():
                self.network.add_device(device_name, device_config.get("type", "router"))
                device = self.network.get_device(device_name)
                
                # Configurar estado del dispositivo
                if not device_config.get("online", True):
                    device.set_offline()
                
                # Recrear interfaces
                for interface_name, interface_config in device_config.get("interfaces", {}).items():
                    device.add_interface(interface_name)
                    interface = device.get_interface(interface_name)
                    
                    # Configurar IP si existe
                    if interface_config.get("ip_address"):
                        interface.set_ip_address(interface_config["ip_address"])
                    
                    # Configurar estado
                    if interface_config.get("is_up", False):
                        interface.no_shutdown()
                    else:
                        interface.shutdown()
            
            # Recrear conexiones
            for connection in config_data.get("connections", []):
                self.network.connect_devices(
                    connection["device1"], connection["interface1"],
                    connection["device2"], connection["interface2"]
                )
            
            return True, f"Configuration loaded successfully from {filepath}"
            
        except json.JSONDecodeError:
            return False, "Invalid JSON format in configuration file"
        except Exception as e:
            return False, f"Error loading configuration: {str(e)}"
    
    def _validate_config_structure(self, config_data):
        """Valida la estructura básica del archivo de configuración"""
        required_keys = ["devices"]
        
        for key in required_keys:
            if key not in config_data:
                return False
        
        # Validar estructura de dispositivos
        if not isinstance(config_data["devices"], dict):
            return False
        
        for device_name, device_config in config_data["devices"].items():
            if not isinstance(device_config, dict):
                return False
            
            if "interfaces" in device_config and not isinstance(device_config["interfaces"], dict):
                return False
        
        return True
    
    def _get_network_connections(self):
        """Obtiene todas las conexiones activas de la red"""
        connections = []
        processed_pairs = set()
        
        for device_name, device in self.network.devices.items():
            for interface_name, interface in device.interfaces.items():
                connected_interfaces = interface.connected_interfaces.to_list()
                
                for connected_if in connected_interfaces:
                    # Crear identificador único para el par de conexión
                    pair_id = tuple(sorted([
                        f"{device_name}:{interface_name}",
                        f"{connected_if.device.name}:{connected_if.name}"
                    ]))
                    
                    if pair_id not in processed_pairs:
                        connections.append({
                            "device1": device_name,
                            "interface1": interface_name,
                            "device2": connected_if.device.name,
                            "interface2": connected_if.name
                        })
                        processed_pairs.add(pair_id)
        
        return connections
    
    def list_config_files(self):
        """Lista todos los archivos de configuración disponibles"""
        try:
            files = [f for f in os.listdir(self.config_dir) if f.endswith('.json')]
            return files
        except Exception:
            return []
    
    def export_to_cisco_format(self, filename=None):
        """Exporta la configuración en formato similar a Cisco IOS"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cisco_config_{timestamp}.txt"
        
        filepath = os.path.join(self.config_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("! Router Simulator Configuration\n")
                f.write(f"! Generated: {datetime.now().isoformat()}\n")
                f.write("!\n")
                
                for device_name, device in self.network.devices.items():
                    f.write(f"!\n! Configuration for {device_name}\n!\n")
                    f.write(f"hostname {device.name}\n")
                    
                    for interface_name, interface in device.interfaces.items():
                        f.write(f"!\ninterface {interface_name}\n")
                        
                        if interface.ip_address:
                            f.write(f" ip address {interface.ip_address}\n")
                        
                        if interface.is_up:
                            f.write(" no shutdown\n")
                        else:
                            f.write(" shutdown\n")
                        
                        f.write("!\n")
                
                # Agregar conexiones como comentarios
                f.write("!\n! Connections\n!\n")
                connections = self._get_network_connections()
                for conn in connections:
                    f.write(f"! connect {conn['device1']} {conn['interface1']} {conn['device2']} {conn['interface2']}\n")
            
            return True, f"Cisco-style configuration exported to {filepath}"
            
        except Exception as e:
            return False, f"Error exporting configuration: {str(e)}"