#!/usr/bin/env python3
"""
Simulador de Red CLI - Aplicación Principal
Router Simulator inspirado en Cisco IOS

Ejecutar con: python main.py
"""

from cli import RouterCLI
from config_manager import ConfigurationManager
import sys
import os
import json

def setup_demo_network(cli):
    """Configura una red de demostración completa con datos de prueba"""
    demo_commands = [
        # Configurar Router1
        "enable",
        "configure terminal",
        "hostname Router1",
        "interface g0/0",
        "ip address 192.168.1.1",
        "no shutdown",
        "exit",
        "interface g0/1", 
        "ip address 10.0.0.1",
        "no shutdown",
        "exit",
        
        # Agregar rutas de prueba (Módulo 1)
        "ip route add 10.0.0.0 255.255.255.0 via 192.168.1.2 metric 10",
        "ip route add 172.16.0.0 255.255.0.0 via 192.168.1.3 metric 5",
        "ip route add 192.168.0.0 255.255.255.0 via 10.0.0.2 metric 1",
        "ip route add 200.200.200.0 255.255.255.0 via 172.16.0.1 metric 15",
        
        # Configurar políticas de prueba (Módulo 3)
        "policy set 10.0.0.0 255.255.0.0 ttl-min 3",
        "policy set 10.0.2.0 255.255.255.0 block",
        "policy set 172.16.0.0 255.255.0.0 ttl-min 5",
        
        "exit",
        
        # Cambiar a Switch1 y configurarlo
        "console Switch1",
        "enable",
        "configure terminal",
        "hostname Switch1",
        "interface g0/1",
        "no shutdown",
        "exit",
        "interface g0/2",
        "no shutdown", 
        "exit",
        "exit",
        
        # Conectar dispositivos
        "connect g0/1 Router1 g0/0",
        "connect g0/2 PC1 eth0",
        
        # Configurar PC2 
        "console PC2",
        "enable",
        "configure terminal",
        "interface eth0",
        "ip address 192.168.1.100",
        "no shutdown",
        "exit",
        "exit",
        
        # Conectar PC2 a Router1
        "connect eth0 Router1 g0/1",
        
        # Volver a Router1 y guardar snapshot de prueba (Módulo 2)
        "console Router1"
    ]
    
    print("Setting up demo network with test data...")
    for command in demo_commands:
        success, message = cli.context.execute_command(command)
        if not success:
            print(f"Demo setup warning: {command} -> {message}")
    
    print("Demo network configured successfully!")
    print("\nNetwork topology:")
    print("PC1 (10.0.0.1) ← eth0 — g0/2 → Switch1 ← g0/1 — g0/0 → Router1 ← g0/1 — eth0 → PC2 (192.168.1.100)")
    print("\nNew commands to try:")
    print("- show ip route")
    print("- show route avl-stats") 
    print("- show ip route-tree")
    print("- show ip prefix-tree")
    print("- show snapshots")
    print("- show error-log")
    print("- btree stats")
    print()

def print_welcome():
    """Imprime mensaje de bienvenida"""
    print("=" * 60)
    print("    SIMULADOR DE RED CLI - ESTILO ROUTER CISCO")
    print()

def create_default_config():
    """Crea un archivo de configuración por defecto"""
    default_config = {
        "metadata": {
            "created_at": "2024-01-01T00:00:00",
            "version": "1.0",
            "description": "Default Router Simulator Configuration"
        },
        "devices": {
            "Router1": {
                "name": "Router1",
                "type": "router",
                "online": True,
                "interfaces": {
                    "g0/0": {
                        "name": "g0/0",
                        "ip_address": "192.168.1.1",
                        "is_up": True,
                        "outgoing_queue_size": 0,
                        "incoming_queue_size": 0
                    },
                    "g0/1": {
                        "name": "g0/1", 
                        "ip_address": "10.0.0.1",
                        "is_up": True,
                        "outgoing_queue_size": 0,
                        "incoming_queue_size": 0
                    }
                }
            },
            "Switch1": {
                "name": "Switch1",
                "type": "switch", 
                "online": True,
                "interfaces": {
                    "g0/1": {
                        "name": "g0/1",
                        "ip_address": None,
                        "is_up": True,
                        "outgoing_queue_size": 0,
                        "incoming_queue_size": 0
                    },
                    "g0/2": {
                        "name": "g0/2",
                        "ip_address": None,
                        "is_up": True,
                        "outgoing_queue_size": 0,
                        "incoming_queue_size": 0
                    }
                }
            },
            "PC1": {
                "name": "PC1",
                "type": "host",
                "online": True,
                "interfaces": {
                    "eth0": {
                        "name": "eth0",
                        "ip_address": "10.0.0.2",
                        "is_up": True,
                        "outgoing_queue_size": 0,
                        "incoming_queue_size": 0
                    }
                }
            },
            "PC2": {
                "name": "PC2", 
                "type": "host",
                "online": True,
                "interfaces": {
                    "eth0": {
                        "name": "eth0",
                        "ip_address": "192.168.1.100",
                        "is_up": True,
                        "outgoing_queue_size": 0,
                        "incoming_queue_size": 0
                    }
                }
            }
        },
        "connections": [
            {"device1": "Router1", "interface1": "g0/0", "device2": "Switch1", "interface2": "g0/1"},
            {"device1": "Switch1", "interface1": "g0/2", "device2": "PC1", "interface2": "eth0"},
            {"device1": "Router1", "interface1": "g0/1", "device2": "PC2", "interface2": "eth0"}
        ],
        "statistics": {
            "total_packets_sent": 0,
            "delivered": 0,
            "dropped_ttl": 0,
            "dropped_firewall": 0,
            "average_hops": 0,
            "top_talker": None
        }
    }
    
    os.makedirs("configs", exist_ok=True)
    
    try:
        with open("configs/default_network.json", 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error creating default config: {e}")
        return False

def main():
    """Función principal del simulador"""
    print_welcome()
    
    # Crear archivo de configuración por defecto si no existe
    if not os.path.exists("configs/default_network.json"):
        print("Creating default network configuration...")
        create_default_config()
    
    # Inicializar simulador sin configuración por defecto
    cli = RouterCLI(load_defaults=False)
    config_manager = ConfigurationManager(cli.network)
    
    # Cargar configuración por defecto al inicio
    print("Loading default network configuration...")
    success, message = config_manager.load_config("default_network.json")
    if success:
        print("✓ Default configuration loaded")
        # Establecer Router1 como dispositivo actual
        cli.context.current_device = cli.network.get_device("Router1")
        # Configurar datos de prueba
        setup_demo_network(cli)
    else:
        print(f"Warning: {message}")
        print("Creating basic default network...")
        cli._setup_default_network()
        cli.context.current_device = cli.network.get_device("Router1")
        # Configurar datos de prueba
        setup_demo_network(cli)
    
    print("\nCommands quick reference:")
    print("• enable                    - Enter privileged mode")
    print("• configure terminal        - Enter configuration mode") 
    print("• interface <name>          - Configure interface")
    print("• ip address <ip>           - Set interface IP")
    print("• ip route add <prefix> <mask> via <next-hop> [metric N] - Add route")
    print("• ip route del <prefix> <mask> - Delete route")
    print("• policy set <prefix> <mask> <ttl-min N | block> - Set policy")
    print("• no shutdown               - Enable interface")
    print("• connect <if1> <dev2> <if2> - Connect devices")
    print("• add device <name> <type>  - Add new device (router/switch/host)")
    print("• send <dest_ip> <message>  - Send packet")
    print("• tick                      - Process network queues")
    print("• show ip route             - Show AVL routing table")
    print("• show route avl-stats      - Show AVL statistics")
    print("• show ip prefix-tree       - Show prefix policies")
    print("• save snapshot <key>       - Save indexed snapshot")
    print("• show snapshots            - List snapshots")
    print("• show error-log            - Show error log")
    print("• console <device>          - Switch to device")
    print("• help                      - Show all commands")
    print("• quit                      - Exit simulator")
    print()
    
    # Actualizar comando save y load para usar el config_manager
    cli.context.config_manager = config_manager
    
    # Configurar datos de prueba adicionales después de cargar
    print("Setting up additional test data...")
    test_commands = [
        "enable", 
        "save snapshot lab-grupoA"
    ]
    
    for command in test_commands:
        success, message = cli.context.execute_command(command)
        if success and message:
            print(f"✓ {message}")
        elif not success:
            print(f"Warning: {command} -> {message}")
    
    # Ejecutar CLI principal
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\nShutting down Router Simulator...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()