"""
Interfaz de línea de comandos (CLI) para el simulador de red
Simula la experiencia de un router profesional con diferentes modos
"""
from network import Network
from commands import *
import shlex

class CLIContext:
    """Contexto del CLI que mantiene el estado actual"""
    
    def __init__(self, network):
        self.network = network
        self.current_device = None
        self.current_mode = "user"  # user, privileged, config, config-if
        self.current_interface = None
        self.running = True
        
        # Registro de comandos por modo
        self.commands = {
            "user": {
                "enable": EnableCommand(),
                "send": SendCommand(),
                "console": ConsoleCommand(),
                "tick": TickCommand(),
                "process": TickCommand(),
                "show": ShowCommand(),
                "list_devices": ListDevicesCommand(),
                "help": HelpCommand(),
                "exit": ExitCommand()
            },
            "privileged": {
                "enable": EnableCommand(),  # Permitir enable en modo privilegiado
                "disable": DisableCommand(),
                "configure": ConfigureTerminalCommand(),
                "connect": ConnectCommand(),
                "disconnect": DisconnectCommand(),
                "set_device_status": SetDeviceStatusCommand(),
                "list_devices": ListDevicesCommand(),
                "show": ShowCommand(),
                "save": SaveSnapshotCommand(),
                "load": LoadConfigCommand(),
                "btree": BtreeStatsCommand(),
                "tick": TickCommand(),
                "process": TickCommand(),
                "console": ConsoleCommand(),
                "help": HelpCommand(),
                "exit": ExitCommand()
            },
            "config": {
                "hostname": HostnameCommand(),
                "interface": InterfaceCommand(),
                "ip": IpCommand(),
                "policy": PolicyCommand(),
                "exit": ExitCommand(),
                "end": EndCommand(),
                "help": HelpCommand()
            },
            "config-if": {
                "ip": IpCommand(),
                "shutdown": ShutdownCommand(),
                "no": NoShutdownCommand(),
                "exit": ExitCommand(),
                "end": EndCommand(),
                "help": HelpCommand()
            }
        }
    
    def get_prompt(self):
        """Genera el prompt basado en el modo actual"""
        if not self.current_device:
            return "Router-Simulator> "
        
        device_name = self.current_device.name
        
        if self.current_mode == "user":
            return f"{device_name}> "
        elif self.current_mode == "privileged":
            return f"{device_name}# "
        elif self.current_mode == "config":
            return f"{device_name}(config)# "
        elif self.current_mode == "config-if":
            return f"{device_name}(config-if)# "
        
        return f"{device_name}> "
    
    def get_available_commands(self):
        """Retorna los comandos disponibles en el modo actual"""
        return self.commands.get(self.current_mode, {})
    
    def parse_command(self, command_line):
        """Parsea una línea de comando y retorna comando y argumentos"""
        try:
            # Usar shlex para manejar comillas correctamente
            parts = shlex.split(command_line.strip())
            if not parts:
                return None, []
            
            command = parts[0].lower()
            args = parts[1:]
            
            # Manejar comandos especiales
            if command == "configure" and len(args) >= 1 and args[0].lower() == "terminal":
                return "configure", ["terminal"]
            elif command == "ip" and len(args) >= 2 and args[0].lower() == "address":
                return "ip", ["address"] + args[1:]
            elif command == "no" and len(args) >= 1:
                # Manejar "no shutdown", "no ip", etc.
                if args[0].lower() == "shutdown":
                    return "no", ["shutdown"]
            elif command == "save" and len(args) >= 1:
                if args[0].lower() == "running-config":
                    return "save", ["running-config"] + args[1:]
                elif args[0].lower() == "snapshot":
                    return "save", ["snapshot"] + args[1:]
            elif command == "load" and len(args) >= 2 and args[0].lower() == "config":
                return "load", ["config"] + args[1:]
            elif command == "ip" and len(args) >= 1:
                if len(args) >= 2 and args[0].lower() == "route":
                    return "ip", ["route"] + args[1:]
                elif len(args) >= 2 and args[0].lower() == "address":
                    return "ip", ["address"] + args[1:]
                else:
                    return "ip", args
            elif command == "show" and len(args) >= 2 and args[0].lower() == "ip" and args[1].lower() == "route-tree":
                return "show", ["ip", "route-tree"]
            elif command == "policy" and len(args) >= 1:
                return "policy", args
            elif command == "btree" and len(args) >= 1 and args[0].lower() == "stats":
                return "btree", ["stats"]
            
            return command, args
            
        except ValueError as e:
            return None, [str(e)]
    
    def execute_command(self, command_line):
        """Ejecuta una línea de comando completa"""
        if not command_line.strip():
            return True, ""
        
        command, args = self.parse_command(command_line)
        
        if command is None:
            return False, f"Invalid command syntax: {args[0] if args else 'empty command'}"
        
        # Comando especial para salir
        if command == "quit" or (command == "exit" and self.current_mode == "user"):
            self.running = False
            return True, "Goodbye!"
        
        available_commands = self.get_available_commands()
        
        if command not in available_commands:
            return False, f"Unknown command '{command}' in {self.current_mode} mode"
        
        try:
            command_obj = available_commands[command]
            return command_obj.execute(self, args)
        except Exception as e:
            # Registrar error en el log
            if self.current_device:
                self.current_device.error_log.log_error("CommandError", str(e), command_line)
            return False, f"Command execution error: {str(e)}"

class RouterCLI:
    """Interfaz principal del CLI del simulador"""
    
    def __init__(self, load_defaults=True):
        self.network = Network()
        self.context = CLIContext(self.network)
        if load_defaults:
            self._setup_default_network()
    
    def _setup_default_network(self):
        """Configura una red de prueba por defecto"""
        # Crear dispositivos por defecto
        self.network.add_device("Router1", "router")
        self.network.add_device("Switch1", "switch")
        self.network.add_device("PC1", "host")
        self.network.add_device("PC2", "host")
        
        # Configurar Router1
        router1 = self.network.get_device("Router1")
        router1.add_interface("g0/0")
        router1.add_interface("g0/1")
        
        # Configurar Switch1
        switch1 = self.network.get_device("Switch1")
        switch1.add_interface("g0/1")
        switch1.add_interface("g0/2")
        
        # Configurar PC1
        pc1 = self.network.get_device("PC1")
        pc1.add_interface("eth0")
        pc1_eth0 = pc1.get_interface("eth0")
        pc1_eth0.set_ip_address("10.0.0.1")
        pc1_eth0.no_shutdown()
        
        # Configurar PC2
        pc2 = self.network.get_device("PC2")
        pc2.add_interface("eth0")
        pc2_eth0 = pc2.get_interface("eth0")
        pc2_eth0.set_ip_address("10.0.0.2")
        pc2_eth0.no_shutdown()
        
        # Establecer dispositivo actual
        self.context.current_device = router1
    
    def run(self):
        """Inicia el bucle principal del CLI"""
        print("Router Simulator CLI v1.0")
        print("Type 'help' for available commands or 'quit' to exit")
        print("Default network loaded with Router1, Switch1, PC1, PC2")
        print()
        
        while self.context.running:
            try:
                prompt = self.context.get_prompt()
                command_line = input(prompt)
                
                success, message = self.context.execute_command(command_line)
                
                if message:
                    if success:
                        print(message)
                    else:
                        print(f"Error: {message}")
                
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
    
    def execute_script(self, commands):
        """Ejecuta una lista de comandos (para testing)"""
        results = []
        for command in commands:
            success, message = self.context.execute_command(command)
            results.append((command, success, message))
        return results

def validate_input(input_str, validation_type):
    """Función de utilidad para validar diferentes tipos de entrada"""
    
    if validation_type == "ip":
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, input_str):
            return False, "Invalid IP address format"
        
        parts = input_str.split('.')
        for part in parts:
            if not (0 <= int(part) <= 255):
                return False, "IP address octets must be between 0-255"
        return True, None
    
    elif validation_type == "hostname":
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-_]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
        if not re.match(pattern, input_str):
            return False, "Invalid hostname format"
        if len(input_str) > 64:
            return False, "Hostname too long (max 64 characters)"
        return True, None
    
    elif validation_type == "interface":
        patterns = [
            r'^g\d+/\d+$',  # GigabitEthernet
            r'^eth\d+$',    # Ethernet
            r'^f\d+/\d+$',  # FastEthernet
            r'^s\d+/\d+$'   # Serial
        ]
        if any(re.match(pattern, input_str) for pattern in patterns):
            return True, None
        return False, "Invalid interface name format"
    
    elif validation_type == "ttl":
        try:
            ttl = int(input_str)
            if 1 <= ttl <= 255:
                return True, None
            return False, "TTL must be between 1 and 255"
        except ValueError:
            return False, "TTL must be a number"
    
    return False, "Unknown validation type"