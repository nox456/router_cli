"""
Implementación del patrón Command para los comandos del CLI
"""
from abc import ABC, abstractmethod
import re

class Command(ABC):
    """Clase base abstracta para todos los comandos"""
    
    @abstractmethod
    def execute(self, cli_context, args):
        """Ejecuta el comando con el contexto y argumentos dados"""
        pass
    
    @abstractmethod
    def get_help(self):
        """Retorna la ayuda del comando"""
        pass

class EnableCommand(Command):
    """Comando enable - cambia a modo privilegiado"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode == "user":
            cli_context.current_mode = "privileged"
            return True, None
        return False, "Already in privileged mode"
    
    def get_help(self):
        return "enable - Enter privileged mode"

class DisableCommand(Command):
    """Comando disable - regresa a modo usuario"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "user":
            cli_context.current_mode = "user"
            return True, None
        return False, "Already in user mode"
    
    def get_help(self):
        return "disable - Return to user mode"

class ConfigureTerminalCommand(Command):
    """Comando configure terminal - entra a modo configuración global"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode == "privileged":
            cli_context.current_mode = "config"
            return True, None
        return False, "Must be in privileged mode"
    
    def get_help(self):
        return "configure terminal - Enter global configuration mode"

class HostnameCommand(Command):
    """Comando hostname - cambia el nombre del dispositivo"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "config":
            return False, "Must be in configuration mode"
        
        if len(args) != 1:
            return False, "Usage: hostname <device_name>"
        
        new_name = args[0]
        if not self._validate_hostname(new_name):
            return False, "Invalid hostname format"
        
        old_name = cli_context.current_device.name
        cli_context.current_device.name = new_name
        
        # Actualizar en la red
        cli_context.network.devices[new_name] = cli_context.network.devices.pop(old_name)
        
        return True, f"Hostname changed to {new_name}"
    
    def _validate_hostname(self, hostname):
        """Valida el formato del hostname"""
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-_]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
        return re.match(pattern, hostname) and len(hostname) <= 64
    
    def get_help(self):
        return "hostname <name> - Set device hostname"

class InterfaceCommand(Command):
    """Comando interface - entra al modo configuración de interfaz"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "config":
            return False, "Must be in configuration mode"
        
        if len(args) != 1:
            return False, "Usage: interface <interface_name>"
        
        interface_name = args[0]
        if not self._validate_interface_name(interface_name):
            return False, "Invalid interface name format"
        
        # Crear interfaz si no existe
        cli_context.current_device.add_interface(interface_name)
        
        cli_context.current_mode = "config-if"
        cli_context.current_interface = interface_name
        
        return True, f"Entered interface {interface_name} configuration"
    
    def _validate_interface_name(self, interface_name):
        """Valida el formato del nombre de interfaz"""
        patterns = [
            r'^g\d+/\d+$',  # GigabitEthernet (g0/0, g1/1, etc.)
            r'^eth\d+$',    # Ethernet (eth0, eth1, etc.)
            r'^f\d+/\d+$',  # FastEthernet (f0/0, f1/1, etc.)
            r'^s\d+/\d+$'   # Serial (s0/0, s1/1, etc.)
        ]
        return any(re.match(pattern, interface_name) for pattern in patterns)
    
    def get_help(self):
        return "interface <name> - Enter interface configuration mode"

class IpAddressCommand(Command):
    """Comando ip address - asigna IP a una interfaz"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "config-if":
            return False, "Must be in interface configuration mode"
        
        if len(args) < 2 or args[0].lower() != "address":
            return False, "Usage: ip address <ip_address>"
        
        ip_address = args[1]
        interface = cli_context.current_device.get_interface(cli_context.current_interface)
        
        if interface.set_ip_address(ip_address):
            return True, f"IP address {ip_address} configured"
        return False, "Invalid IP address format"
    
    def get_help(self):
        return "ip address <ip> - Set interface IP address"

class ShutdownCommand(Command):
    """Comando shutdown - desactiva una interfaz"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "config-if":
            return False, "Must be in interface configuration mode"
        
        interface = cli_context.current_device.get_interface(cli_context.current_interface)
        interface.shutdown()
        
        return True, f"Interface {cli_context.current_interface} shutdown"
    
    def get_help(self):
        return "shutdown - Disable interface"

class NoShutdownCommand(Command):
    """Comando no shutdown - activa una interfaz"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "config-if":
            return False, "Must be in interface configuration mode"
        
        interface = cli_context.current_device.get_interface(cli_context.current_interface)
        interface.no_shutdown()
        
        return True, f"Interface {cli_context.current_interface} is up"
    
    def get_help(self):
        return "no shutdown - Enable interface"

class ExitCommand(Command):
    """Comando exit - retrocede un nivel de modo"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode == "config-if":
            cli_context.current_mode = "config"
            cli_context.current_interface = None
            return True, "Exited interface configuration mode"
        elif cli_context.current_mode == "config":
            cli_context.current_mode = "privileged"
            return True, "Exited global configuration mode"
        elif cli_context.current_mode == "privileged":
            cli_context.current_mode = "user"
            return True, "Exited privileged mode"
        else:
            return False, "Cannot exit from user mode"
    
    def get_help(self):
        return "exit - Exit current configuration mode"

class EndCommand(Command):
    """Comando end - sale directamente a modo privilegiado"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode in ["config", "config-if"]:
            cli_context.current_mode = "privileged"
            cli_context.current_interface = None
            return True, "Returned to privileged mode"
        return False, "Already in privileged or user mode"
    
    def get_help(self):
        return "end - Return directly to privileged mode"

class ConnectCommand(Command):
    """Comando connect - conecta dos interfaces de dispositivos"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "privileged":
            return False, "Must be in privileged mode"
        
        if len(args) != 3:
            return False, "Usage: connect <interface1> <device2> <interface2>"
        
        interface1, device2_name, interface2 = args
        device1_name = cli_context.current_device.name
        
        if cli_context.network.connect_devices(device1_name, interface1, device2_name, interface2):
            return True, f"Connected {device1_name}:{interface1} to {device2_name}:{interface2}"
        return False, "Failed to connect devices"
    
    def get_help(self):
        return "connect <iface1> <device2> <iface2> - Connect two device interfaces"

class DisconnectCommand(Command):
    """Comando disconnect - desconecta dos interfaces"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "privileged":
            return False, "Must be in privileged mode"
        
        if len(args) != 3:
            return False, "Usage: disconnect <interface1> <device2> <interface2>"
        
        interface1, device2_name, interface2 = args
        device1_name = cli_context.current_device.name
        
        if cli_context.network.disconnect_devices(device1_name, interface1, device2_name, interface2):
            return True, f"Disconnected {device1_name}:{interface1} from {device2_name}:{interface2}"
        return False, "Failed to disconnect devices"
    
    def get_help(self):
        return "disconnect <iface1> <device2> <iface2> - Disconnect two device interfaces"

class ListDevicesCommand(Command):
    """Comando list_devices - lista todos los dispositivos"""
    
    def execute(self, cli_context, args):
        devices = cli_context.network.list_devices()
        return True, "Devices in network:\n" + "\n".join(devices)
    
    def get_help(self):
        return "list_devices - List all devices in the network"

class SendCommand(Command):
    """Comando send - envía un paquete"""
    
    def execute(self, cli_context, args):
        if len(args) < 2:
            return False, "Usage: send <destination_ip> <message> [ttl]"
        
        destination_ip = args[0]
        message = args[1]
        ttl = int(args[2]) if len(args) > 2 else 64
        
        # Buscar interfaz de origen
        source_ip = None
        for interface in cli_context.current_device.interfaces.values():
            if interface.ip_address and interface.is_up:
                source_ip = interface.ip_address
                break
        
        if not source_ip:
            return False, "No active interface with IP address found"
        
        if cli_context.current_device.send_packet(source_ip, destination_ip, message, ttl):
            cli_context.network.statistics.update_packet_sent(cli_context.current_device.name)
            return True, "Message queued for delivery"
        return False, "Failed to send packet"
    
    def get_help(self):
        return "send <dest_ip> <message> [ttl] - Send a packet to destination"

class TickCommand(Command):
    """Comando tick/process - avanza la simulación un paso"""
    
    def execute(self, cli_context, args):
        results = cli_context.network.tick()
        if results:
            return True, "\n".join(results)
        return True, "No packets to process"
    
    def get_help(self):
        return "tick/process - Advance simulation one step"

class ShowCommand(Command):
    """Comando show - muestra información del sistema"""
    
    def execute(self, cli_context, args):
        if len(args) == 0:
            return False, "Usage: show <subcommand>"
        
        subcommand = args[0].lower()
        
        if subcommand == "history":
            device_name = args[1] if len(args) > 1 else cli_context.current_device.name
            device = cli_context.network.get_device(device_name)
            if not device:
                return False, f"Device {device_name} not found"
            
            history = device.get_message_history()
            if not history:
                return True, f"No message history for {device_name}"
            
            result = f"Message history for {device_name}:\n"
            for i, packet in enumerate(history, 1):
                ttl_status = "TTL expired" if packet.dropped and packet.drop_reason == "TTL expired" else "No"
                result += f"{i}) From {packet.source_ip} to {packet.destination_ip}: \"{packet.content}\" | "
                result += f"TTL at arrival: {packet.ttl} | Path: {packet.get_route_trace_string()}\n"
            
            return True, result.strip()
        
        elif subcommand == "queue":
            device_name = args[1] if len(args) > 1 else cli_context.current_device.name
            device = cli_context.network.get_device(device_name)
            if not device:
                return False, f"Device {device_name} not found"
            
            queue_status = device.get_queue_status()
            result = f"Queue status for {device_name}:\n"
            
            for interface_name, queues in queue_status.items():
                result += f"Interface {interface_name}:\n"
                result += f"  Outgoing: {len(queues['outgoing'])} packets\n"
                result += f"  Incoming: {len(queues['incoming'])} packets\n"
            
            return True, result.strip()
        
        elif subcommand == "interfaces":
            device = cli_context.current_device
            interfaces_status = device.get_interfaces_status()
            
            result = f"Interfaces for {device.name}:\n"
            for name, status in interfaces_status.items():
                state = "up" if status['is_up'] else "down"
                ip = status['ip_address'] or "unassigned"
                connections = ", ".join(status['connected_to']) or "none"
                result += f"  {name}: {state} | IP: {ip} | Connected to: {connections}\n"
            
            return True, result.strip()
        
        elif subcommand == "statistics":
            stats = cli_context.network.get_network_statistics()
            result = "Network Statistics:\n"
            result += f"Total packets sent: {stats['total_packets_sent']}\n"
            result += f"Delivered: {stats['delivered']}\n"
            result += f"Dropped (TTL): {stats['dropped_ttl']}\n"
            result += f"Dropped (Firewall): {stats['dropped_firewall']}\n"
            result += f"Average hops: {stats['average_hops']}\n"
            if stats['top_talker']:
                result += f"Top talker: {stats['top_talker']}"
            
            return True, result.strip()
        
        elif subcommand == "ip" and len(args) > 1:
            if args[1] == "route":
                device = cli_context.current_device
                routes = device.routing_table.in_order_traversal()
                
                if not routes:
                    return True, "No routes configured\nDefault: none"
                
                result = "Routing table:\n"
                for route in routes:
                    result += f"{route.to_cidr()} via {route.next_hop} metric {route.metric}\n"
                result += "Default: none"
                
                return True, result.strip()
            elif args[1] == "prefix-tree":
                tree_display = cli_context.current_device.prefix_trie.display_tree()
                return True, tree_display
            elif args[1] == "route-tree":
                tree_display = cli_context.current_device.routing_table.get_tree_display()
                return True, tree_display
        
        elif subcommand == "route" and len(args) > 1:
            if args[1] == "avl-stats":
                return ShowRouteAvlStatsCommand().execute(cli_context, [])
        
        elif subcommand == "snapshots":
            return ShowSnapshotsCommand().execute(cli_context, [])
        
        elif subcommand == "error-log":
            limit_args = args[1:] if len(args) > 1 else []
            return ShowErrorLogCommand().execute(cli_context, limit_args)
        
        
        else:
            return False, f"Unknown show subcommand: {subcommand}"
    
    def get_help(self):
        return "show <history|queue|interfaces|statistics|ip|route|snapshots|error-log> - Show system information"

class SetDeviceStatusCommand(Command):
    """Comando set_device_status - cambia estado online/offline"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "privileged":
            return False, "Must be in privileged mode"
        
        if len(args) != 2:
            return False, "Usage: set_device_status <device> <online|offline>"
        
        device_name, status = args
        
        if status.lower() not in ["online", "offline"]:
            return False, "Status must be 'online' or 'offline'"
        
        if cli_context.network.set_device_status(device_name, status):
            return True, f"Device {device_name} set to {status}"
        return False, f"Device {device_name} not found"
    
    def get_help(self):
        return "set_device_status <device> <online|offline> - Change device status"

class SaveConfigCommand(Command):
    """Comando save running-config - guarda la configuración"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "privileged":
            return False, "Must be in privileged mode"
        
        filename = args[0] if args else "running-config.json"
        
        if cli_context.network.save_configuration(filename):
            return True, f"Configuration saved to {filename}"
        return False, "Failed to save configuration"
    
    def get_help(self):
        return "save running-config [filename] - Save current configuration"

class LoadConfigCommand(Command):
    """Comando load config - carga una configuración"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "privileged":
            return False, "Must be in privileged mode"
        
        if len(args) != 1:
            return False, "Usage: load config <filename>"
        
        filename = args[0]
        
        if cli_context.network.load_configuration(filename):
            return True, f"Configuration loaded from {filename}"
        return False, f"Failed to load configuration from {filename}"
    
    def get_help(self):
        return "load config <filename> - Load configuration from file"

class ConsoleCommand(Command):
    """Comando console - cambia el dispositivo activo"""
    
    def execute(self, cli_context, args):
        if len(args) != 1:
            return False, "Usage: console <device_name>"
        
        device_name = args[0]
        device = cli_context.network.get_device(device_name)
        
        if not device:
            return False, f"Device {device_name} not found"
        
        cli_context.current_device = device
        cli_context.current_mode = "user"
        cli_context.current_interface = None
        
        return True, f"Switched to {device_name}"
    
    def get_help(self):
        return "console <device> - Switch to device console"

class HelpCommand(Command):
    """Comando help - muestra ayuda de comandos"""
    
    def execute(self, cli_context, args):
        commands = cli_context.get_available_commands()
        help_text = "Available commands:\n"
        
        for cmd_name, cmd_obj in commands.items():
            help_text += f"  {cmd_obj.get_help()}\n"
        
        return True, help_text.strip()
    
    def get_help(self):
        return "help - Show available commands"

class IpCommand(Command):
    """Comando ip - maneja subcomandos de IP"""
    
    def execute(self, cli_context, args):
        if len(args) < 1:
            return False, "Usage: ip <subcommand>"
        
        subcommand = args[0].lower()
        
        if subcommand == "address" and cli_context.current_mode == "config-if":
            return IpAddressCommand().execute(cli_context, args)
        
        elif subcommand == "route" and cli_context.current_mode == "config":
            if len(args) < 2:
                return False, "Usage: ip route <add|del>"
            
            action = args[1].lower()
            if action == "add":
                return self._handle_route_add(cli_context, args[2:])
            elif action == "del":
                return self._handle_route_del(cli_context, args[2:])
            else:
                return False, "Usage: ip route <add|del>"
        
        else:
            return False, f"Unknown ip subcommand: {subcommand}"
    
    def _handle_route_add(self, cli_context, args):
        """Maneja ip route add"""
        if len(args) < 4:
            return False, "Usage: ip route add <prefix> <mask> via <next-hop> [metric N]"
        
        prefix = args[0]
        mask = args[1]
        
        if args[2] != "via":
            return False, "Usage: ip route add <prefix> <mask> via <next-hop> [metric N]"
        
        next_hop = args[3]
        metric = 0
        
        if len(args) > 4 and args[4] == "metric":
            if len(args) > 5:
                try:
                    metric = int(args[5])
                except ValueError:
                    return False, "Metric must be a number"
        
        cli_context.current_device.routing_table.insert(prefix, mask, next_hop, metric)
        return True, f"Route {prefix}/{self._mask_to_cidr(mask)} via {next_hop} metric {metric} added"
    
    def _handle_route_del(self, cli_context, args):
        """Maneja ip route del"""
        if len(args) < 2:
            return False, "Usage: ip route del <prefix> <mask>"
        
        prefix = args[0]
        mask = args[1]
        
        # Verificar que existe antes de eliminar
        routes = cli_context.current_device.routing_table.in_order_traversal()
        route_exists = any(r.prefix == prefix and r.mask == mask for r in routes)
        
        if not route_exists:
            cli_context.current_device.error_log.log_error("RouteNotFound", f"Route {prefix}/{self._mask_to_cidr(mask)} not found")
            return False, f"Route {prefix}/{self._mask_to_cidr(mask)} not found"
        
        cli_context.current_device.routing_table.delete(prefix, mask)
        return True, f"Route {prefix}/{self._mask_to_cidr(mask)} deleted"
    
    def _mask_to_cidr(self, mask):
        """Convierte máscara a notación CIDR"""
        cidr = 0
        for octet in mask.split('.'):
            cidr += bin(int(octet)).count('1')
        return cidr
    
    def get_help(self):
        return "ip <address|route> - IP configuration commands"


class ShowIpRouteCommand(Command):
    """Comando show ip route - muestra tabla de rutas AVL"""
    
    def execute(self, cli_context, args):
        device = cli_context.current_device
        routes = device.routing_table.in_order_traversal()
        
        if not routes:
            return True, "No routes configured\nDefault: none"
        
        result = "Routing table:\n"
        for route in routes:
            result += f"{route.to_cidr()} via {route.next_hop} metric {route.metric}\n"
        result += "Default: none"
        
        return True, result.strip()
    
    def get_help(self):
        return "show ip route - Display AVL routing table"

class ShowRouteAvlStatsCommand(Command):
    """Comando show route avl-stats - muestra estadísticas del AVL"""
    
    def execute(self, cli_context, args):
        avl = cli_context.current_device.routing_table
        stats = avl.stats
        
        result = f"nodes={avl.size} height={avl.get_height(avl.root)} "
        result += f"rotations: LL={stats['rotations_ll']} LR={stats['rotations_lr']} "
        result += f"RL={stats['rotations_rl']} RR={stats['rotations_rr']}"
        
        return True, result
    
    def get_help(self):
        return "show route avl-stats - Display AVL tree statistics"


class SaveSnapshotCommand(Command):
    """Comando save snapshot - guarda snapshot indexado"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "privileged":
            return False, "Must be in privileged mode"
        
        if len(args) < 2 or args[0] != "snapshot":
            return False, "Usage: save snapshot <key>"
        
        key = args[1]
        success, result = cli_context.current_device.save_snapshot(key)
        
        if success:
            return True, f"[OK] snapshot {key} -> file: {result} (indexed)"
        return False, result
    
    def get_help(self):
        return "save snapshot <key> - Save and index snapshot"

class LoadConfigCommand(Command):
    """Comando load config - carga configuración desde B-tree"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "privileged":
            return False, "Must be in privileged mode"
        
        if len(args) < 2 or args[0] != "config":
            return False, "Usage: load config <key>"
        
        key = args[1]
        success, result = cli_context.current_device.load_snapshot(key)
        return success, result
    
    def get_help(self):
        return "load config <key> - Load configuration from B-tree index"

class ShowSnapshotsCommand(Command):
    """Comando show snapshots - lista snapshots del B-tree"""
    
    def execute(self, cli_context, args):
        snapshots = cli_context.current_device.snapshot_index.in_order_traversal()
        
        if not snapshots:
            return True, "No snapshots found"
        
        result = "Snapshots:\n"
        for key, filename in snapshots:
            result += f"{key} -> {filename}\n"
        
        return True, result.strip()
    
    def get_help(self):
        return "show snapshots - List B-tree indexed snapshots"

class BtreeStatsCommand(Command):
    """Comando btree stats - estadísticas del B-tree"""
    
    def execute(self, cli_context, args):
        btree = cli_context.current_device.snapshot_index
        stats = btree.stats
        
        result = f"order={btree.order} height={stats['height']} "
        result += f"nodes={stats['nodes']} splits={stats['splits']} merges={stats['merges']}"
        
        return True, result
    
    def get_help(self):
        return "btree stats - Display B-tree statistics"

class PolicyCommand(Command):
    """Comando policy - maneja políticas del trie"""
    
    def execute(self, cli_context, args):
        if cli_context.current_mode != "config":
            return False, "Must be in configuration mode"
        
        if len(args) < 1:
            return False, "Usage: policy <set|unset>"
        
        action = args[0].lower()
        
        if action == "set":
            return self._handle_policy_set(cli_context, args[1:])
        elif action == "unset":
            return self._handle_policy_unset(cli_context, args[1:])
        else:
            return False, "Usage: policy <set|unset>"
    
    def _handle_policy_set(self, cli_context, args):
        """Maneja policy set"""
        if len(args) < 3:
            return False, "Usage: policy set <prefix> <mask> <ttl-min N | block>"
        
        prefix = args[0]
        mask = args[1]
        
        if args[2] == "block":
            cli_context.current_device.prefix_trie.set_policy(prefix, mask, "block", True)
            return True, f"Block policy set for {prefix}/{self._mask_to_cidr(mask)}"
        
        elif args[2] == "ttl-min" and len(args) > 3:
            try:
                ttl_min = int(args[3])
                cli_context.current_device.prefix_trie.set_policy(prefix, mask, "ttl-min", ttl_min)
                return True, f"TTL minimum {ttl_min} set for {prefix}/{self._mask_to_cidr(mask)}"
            except ValueError:
                return False, "TTL minimum must be a number"
        
        return False, "Usage: policy set <prefix> <mask> <ttl-min N | block>"
    
    def _handle_policy_unset(self, cli_context, args):
        """Maneja policy unset"""
        if len(args) < 2:
            return False, "Usage: policy unset <prefix> <mask>"
        
        prefix = args[0]
        mask = args[1]
        
        # Para simplificar, recreamos el nodo sin políticas
        cli_context.current_device.prefix_trie.insert_prefix(prefix, mask, {})
        return True, f"Policies removed for {prefix}/{self._mask_to_cidr(mask)}"
    
    def _mask_to_cidr(self, mask):
        """Convierte máscara a notación CIDR"""
        cidr = 0
        for octet in mask.split('.'):
            cidr += bin(int(octet)).count('1')
        return cidr
    
    def get_help(self):
        return "policy <set|unset> - Configure prefix policies"


class ShowErrorLogCommand(Command):
    """Comando show error-log - muestra log de errores"""
    
    def execute(self, cli_context, args):
        limit = None
        if args and len(args) > 0:
            try:
                limit = int(args[0])
            except ValueError:
                return False, "Limit must be a number"
        
        errors = cli_context.current_device.error_log.get_errors(limit)
        
        if not errors:
            return True, "No errors logged"
        
        result = "Error Log:\n"
        for error in errors:
            result += f"[{error.timestamp}] {error.error_type}: {error.message}"
            if error.command:
                result += f" (Command: {error.command})"
            result += "\n"
        
        return True, result.strip()
    
    def get_help(self):
        return "show error-log [n] - Display error log (optional limit)"