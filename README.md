# Simulador de Red CLI - Estilo Router

Simulador de red de área local (LAN) con interfaz de línea de comandos inspirada en routers Cisco IOS.

## Características Implementadas

### ✅ Módulo 1: Dispositivos y Red (4 ptos)
- Clase `Device` con interfaces configurables
- Clase `Network` para gestión de topología
- Soporte para tipos: router, switch, host, firewall
- Interfaces con nombres estándar (g0/0, eth0, etc.)
- Estados de interfaz (up/down) y dispositivo (online/offline)

### ✅ Módulo 2: Paquetes y Comunicación (4 ptos)
- Clase `Packet` con TTL y trazado de ruta
- Sistema de colas para procesamiento de paquetes
- Comando `send` para envío de mensajes
- Comando `tick`/`process` para avanzar simulación

### ✅ Módulo 3: Estructuras de Datos (3 ptos)
- **Lista enlazada** - Almacena vecinos de interfaces
- **Cola (Queue)** - Gestiona paquetes entrantes/salientes 
- **Pila (Stack)** - Historial de mensajes recibidos
- Todas implementadas desde cero sin usar librerías

### ✅ Módulo 4: Interfaz CLI (3 ptos)
- Múltiples modos: usuario (`>`), privilegiado (`#`), configuración
- Patrón Command para todos los comandos
- Parser robusto con validación de sintaxis
- Manejo de errores y retroalimentación clara

### ✅ Módulo 5: Estadísticas y Reportes (3 ptos)
- `show history` - Historial de paquetes por dispositivo
- `show queue` - Estado de colas de interfaces
- `show interfaces` - Configuración de interfaces
- `show statistics` - Métricas globales de red

### ✅ Módulo 6: Persistencia (3 ptos)
- Guardado/carga en formato JSON
- `save running-config` y `load config`
- Configuración por defecto incluida
- Export a formato tipo Cisco IOS

### ✅ Requisitos Adicionales
- ✅ Validación de datos de usuario
- ✅ Guardado en archivos JSON
- ✅ Datos por defecto para pruebas
- ✅ Código comentado
- ✅ Paradigma orientado a objetos

## Instalación y Uso

```bash
# Clonar o descargar el proyecto
cd router_cli

# Ejecutar el simulador
python main.py
```

## Comandos Principales

### Modo Usuario (`Device>`)
```
send <dest_ip> <message> [ttl]  # Enviar paquete
console <device>                # Cambiar a otro dispositivo
enable                          # Entrar a modo privilegiado
help                           # Mostrar ayuda
```

### Modo Privilegiado (`Device#`)
```
configure terminal             # Entrar a configuración global
connect <if1> <dev2> <if2>    # Conectar interfaces
disconnect <if1> <dev2> <if2> # Desconectar interfaces
set_device_status <dev> <online|offline>
list_devices                  # Listar todos los dispositivos
show <history|queue|interfaces|statistics>
tick / process               # Avanzar simulación
save running-config [file]   # Guardar configuración
load config <file>           # Cargar configuración
```

### Modo Configuración Global (`Device(config)#`)
```
hostname <name>              # Cambiar nombre del dispositivo
interface <name>             # Configurar interfaz específica
```

### Modo Configuración Interfaz (`Device(config-if)#`)
```
ip address <ip>             # Asignar dirección IP
shutdown                    # Desactivar interfaz
no shutdown                 # Activar interfaz
```

## Ejemplo de Sesión

```
Router1> enable
Router1# configure terminal
Router1(config)# hostname MainRouter
MainRouter(config)# interface g0/0
MainRouter(config-if)# ip address 192.168.1.1
MainRouter(config-if)# no shutdown
MainRouter(config-if)# exit
MainRouter(config)# exit
MainRouter# connect g0/0 Switch1 g0/1
MainRouter# console PC1
PC1> send 192.168.1.1 "Hello Router!" 5
Message queued for delivery.
PC1> tick
[Tick] PC1 → Switch1: packet forwarded (TTL=4)
PC1> console MainRouter
MainRouter# tick
[Tick] MainRouter: packet delivered from 10.0.0.1
MainRouter# show history
Message history for MainRouter:
1) From 10.0.0.1 to 192.168.1.1: "Hello Router!" | TTL at arrival: 3 | Path: PC1 → Switch1 → MainRouter
```

## Estructura del Proyecto

```
router_cli/
├── main.py              # Aplicación principal
├── cli.py               # Interfaz de línea de comandos
├── commands.py          # Implementación patrón Command
├── device.py            # Clases Device e Interface
├── network.py           # Clase Network y estadísticas
├── packet.py            # Clase Packet con TTL
├── data_structures.py   # Estructuras de datos desde cero
├── config_manager.py    # Gestor de configuración
├── configs/             # Directorio de configuraciones
│   └── default_network.json
└── README.md
```

## Características Técnicas

- **Lenguaje**: Python 3.7+
- **Paradigma**: Programación Orientada a Objetos
- **Estructuras**: Implementadas desde cero (sin usar librerías)
- **Validación**: Completa validación de entrada de usuario
- **Persistencia**: Formato JSON para configuraciones
- **CLI**: Múltiples modos con parser robusto

## Testing

El simulador incluye datos de prueba por defecto:
- Router1 con interfaces g0/0 y g0/1
- Switch1 con interfaces g0/1 y g0/2  
- PC1 y PC2 como hosts
- Configuración de red precargada

## Notas de Implementación

- Las colas procesan paquetes en orden FIFO
- El historial usa pila LIFO (último recibido, primero mostrado)
- TTL decrementa en cada salto, paquete se descarta en TTL=0
- Validación robusta de IPs, hostnames e interfaces
- Soporte para reconexión en caliente de dispositivos