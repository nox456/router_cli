"""
Clase Packet para representar paquetes de red con TTL y trazado de ruta
"""
import uuid
from data_structures import LinkedList

class Packet:
    """Paquete de red virtual con origen, destino, contenido y TTL"""
    
    def __init__(self, source_ip, destination_ip, content, ttl=64):
        """
        Inicializa un nuevo paquete
        
        Args:
            source_ip (str): Dirección IP de origen
            destination_ip (str): Dirección IP de destino
            content (str): Contenido del mensaje
            ttl (int): Time To Live inicial
        """
        self.id = str(uuid.uuid4())[:8]  # Identificador único corto
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.content = content
        self.ttl = ttl
        self.original_ttl = ttl
        self.route_trace = LinkedList()  # Traza de la ruta seguida
        self.delivered = False
        self.dropped = False
        self.drop_reason = None
    
    def add_hop(self, device_name):
        """Agrega un dispositivo a la traza de ruta"""
        self.route_trace.append(device_name)
    
    def decrement_ttl(self):
        """Decrementa el TTL en 1 y retorna True si aún es válido"""
        self.ttl -= 1
        if self.ttl <= 0:
            self.dropped = True
            self.drop_reason = "TTL expired"
            return False
        return True
    
    def get_route_trace_string(self):
        """Retorna la traza de ruta como string"""
        hops = self.route_trace.to_list()
        return " → ".join(hops) if hops else "No hops recorded"
    
    def mark_delivered(self):
        """Marca el paquete como entregado exitosamente"""
        self.delivered = True
    
    def mark_dropped(self, reason):
        """Marca el paquete como descartado con una razón"""
        self.dropped = True
        self.drop_reason = reason
    
    def get_hops_count(self):
        """Retorna el número de saltos realizados"""
        return len(self.route_trace)
    
    def to_dict(self):
        """Convierte el paquete a diccionario para serialización"""
        return {
            'id': self.id,
            'source_ip': self.source_ip,
            'destination_ip': self.destination_ip,
            'content': self.content,
            'ttl': self.ttl,
            'original_ttl': self.original_ttl,
            'route_trace': self.route_trace.to_list(),
            'delivered': self.delivered,
            'dropped': self.dropped,
            'drop_reason': self.drop_reason
        }
    
    def __str__(self):
        """Representación string del paquete"""
        status = "Delivered" if self.delivered else ("Dropped" if self.dropped else "In transit")
        return f"Packet {self.id}: {self.source_ip} → {self.destination_ip} | TTL: {self.ttl} | Status: {status}"