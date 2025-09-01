"""
Estructuras de datos implementadas desde cero para el simulador de red
Incluye: Lista enlazada, Cola (Queue), Pila (Stack), AVL Tree, B-tree y Trie
"""

class Node:
    """Nodo básico para estructuras de datos enlazadas"""
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    """Lista enlazada para almacenar vecinos de interfaces"""
    def __init__(self):
        self.head = None
        self.size = 0
    
    def append(self, data):
        """Agrega un elemento al final de la lista"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1
    
    def remove(self, data):
        """Remueve un elemento de la lista"""
        if not self.head:
            return False
        
        if self.head.data == data:
            self.head = self.head.next
            self.size -= 1
            return True
        
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        return False
    
    def find(self, data):
        """Busca un elemento en la lista"""
        current = self.head
        while current:
            if current.data == data:
                return current.data
            current = current.next
        return None
    
    def to_list(self):
        """Convierte la lista enlazada a una lista de Python"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def is_empty(self):
        """Verifica si la lista está vacía"""
        return self.head is None
    
    def __len__(self):
        return self.size

class Queue:
    """Cola (FIFO) para gestionar paquetes entrantes y salientes"""
    def __init__(self):
        self.front = None
        self.rear = None
        self.size = 0
    
    def enqueue(self, data):
        """Agrega un elemento al final de la cola"""
        new_node = Node(data)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self.size += 1
    
    def dequeue(self):
        """Remueve y retorna el elemento del frente de la cola"""
        if self.is_empty():
            return None
        
        data = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self.size -= 1
        return data
    
    def peek(self):
        """Retorna el elemento del frente sin removerlo"""
        if self.is_empty():
            return None
        return self.front.data
    
    def is_empty(self):
        """Verifica si la cola está vacía"""
        return self.front is None
    
    def to_list(self):
        """Convierte la cola a una lista de Python para visualización"""
        result = []
        current = self.front
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def __len__(self):
        return self.size

class Stack:
    """Pila (LIFO) para el historial de mensajes recibidos"""
    def __init__(self):
        self.top = None
        self.size = 0
    
    def push(self, data):
        """Agrega un elemento al tope de la pila"""
        new_node = Node(data)
        new_node.next = self.top
        self.top = new_node
        self.size += 1
    
    def pop(self):
        """Remueve y retorna el elemento del tope de la pila"""
        if self.is_empty():
            return None
        
        data = self.top.data
        self.top = self.top.next
        self.size -= 1
        return data
    
    def peek(self):
        """Retorna el elemento del tope sin removerlo"""
        if self.is_empty():
            return None
        return self.top.data
    
    def is_empty(self):
        """Verifica si la pila está vacía"""
        return self.top is None
    
    def to_list(self):
        """Convierte la pila a una lista de Python para visualización"""
        result = []
        current = self.top
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def __len__(self):
        return self.size

class AVLNode:
    """Nodo para el árbol AVL de rutas"""
    def __init__(self, prefix, mask, next_hop, metric=0):
        self.prefix = prefix
        self.mask = mask
        self.next_hop = next_hop
        self.metric = metric
        self.height = 1
        self.left = None
        self.right = None
    
    def to_cidr(self):
        """Convierte la ruta a notación CIDR"""
        cidr_bits = bin(int(self.mask.split('.')[0])).count('1') + \
                   bin(int(self.mask.split('.')[1])).count('1') + \
                   bin(int(self.mask.split('.')[2])).count('1') + \
                   bin(int(self.mask.split('.')[3])).count('1')
        return f"{self.prefix}/{cidr_bits}"

class AVLTree:
    """Árbol AVL para tabla de rutas balanceada"""
    def __init__(self):
        self.root = None
        self.size = 0
        self.stats = {
            'rotations_ll': 0,
            'rotations_lr': 0,
            'rotations_rl': 0,
            'rotations_rr': 0
        }
    
    def get_height(self, node):
        """Obtiene la altura de un nodo"""
        if not node:
            return 0
        return node.height
    
    def get_balance(self, node):
        """Obtiene el factor de balance de un nodo"""
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)
    
    def update_height(self, node):
        """Actualiza la altura de un nodo"""
        if node:
            node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
    
    def rotate_right(self, z):
        """Rotación simple a la derecha (LL)"""
        self.stats['rotations_ll'] += 1
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        self.update_height(z)
        self.update_height(y)
        
        return y
    
    def rotate_left(self, z):
        """Rotación simple a la izquierda (RR)"""
        self.stats['rotations_rr'] += 1
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        self.update_height(z)
        self.update_height(y)
        
        return y
    
    def rotate_left_right(self, z):
        """Rotación doble izquierda-derecha (LR)"""
        self.stats['rotations_lr'] += 1
        z.left = self.rotate_left(z.left)
        return self.rotate_right(z)
    
    def rotate_right_left(self, z):
        """Rotación doble derecha-izquierda (RL)"""
        self.stats['rotations_rl'] += 1
        z.right = self.rotate_right(z.right)
        return self.rotate_left(z)
    
    def _compare_routes(self, route1, route2):
        """Compara dos rutas para el ordenamiento en AVL"""
        prefix1, mask1, metric1 = route1
        prefix2, mask2, metric2 = route2
        
        if prefix1 != prefix2:
            return -1 if prefix1 < prefix2 else 1
        if mask1 != mask2:
            return -1 if mask1 < mask2 else 1
        return -1 if metric1 < metric2 else (1 if metric1 > metric2 else 0)
    
    def insert(self, prefix, mask, next_hop, metric=0):
        """Inserta una ruta en el árbol AVL"""
        self.root = self._insert_node(self.root, prefix, mask, next_hop, metric)
        self.size += 1
    
    def _insert_node(self, node, prefix, mask, next_hop, metric):
        """Método auxiliar para insertar nodo"""
        if not node:
            return AVLNode(prefix, mask, next_hop, metric)
        
        comp = self._compare_routes((prefix, mask, metric), (node.prefix, node.mask, node.metric))
        
        if comp < 0:
            node.left = self._insert_node(node.left, prefix, mask, next_hop, metric)
        elif comp > 0:
            node.right = self._insert_node(node.right, prefix, mask, next_hop, metric)
        else:
            node.next_hop = next_hop
            node.metric = metric
            return node
        
        self.update_height(node)
        balance = self.get_balance(node)
        
        if balance > 1 and self._compare_routes((prefix, mask, metric), (node.left.prefix, node.left.mask, node.left.metric)) < 0:
            return self.rotate_right(node)
        
        if balance < -1 and self._compare_routes((prefix, mask, metric), (node.right.prefix, node.right.mask, node.right.metric)) > 0:
            return self.rotate_left(node)
        
        if balance > 1 and self._compare_routes((prefix, mask, metric), (node.left.prefix, node.left.mask, node.left.metric)) > 0:
            return self.rotate_left_right(node)
        
        if balance < -1 and self._compare_routes((prefix, mask, metric), (node.right.prefix, node.right.mask, node.right.metric)) < 0:
            return self.rotate_right_left(node)
        
        return node
    
    def delete(self, prefix, mask):
        """Elimina una ruta del árbol AVL"""
        self.root = self._delete_node(self.root, prefix, mask)
        self.size = max(0, self.size - 1)
    
    def _delete_node(self, node, prefix, mask):
        """Método auxiliar para eliminar nodo"""
        if not node:
            return node
        
        comp = self._compare_routes((prefix, mask, 0), (node.prefix, node.mask, 0))
        
        if comp < 0:
            node.left = self._delete_node(node.left, prefix, mask)
        elif comp > 0:
            node.right = self._delete_node(node.right, prefix, mask)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            
            temp = self._find_min(node.right)
            node.prefix = temp.prefix
            node.mask = temp.mask
            node.next_hop = temp.next_hop
            node.metric = temp.metric
            node.right = self._delete_node(node.right, temp.prefix, temp.mask)
        
        self.update_height(node)
        balance = self.get_balance(node)
        
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)
        
        if balance > 1 and self.get_balance(node.left) < 0:
            return self.rotate_left_right(node)
        
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)
        
        if balance < -1 and self.get_balance(node.right) > 0:
            return self.rotate_right_left(node)
        
        return node
    
    def _find_min(self, node):
        """Encuentra el nodo con valor mínimo"""
        while node.left:
            node = node.left
        return node
    
    def lookup(self, dest_ip):
        """Busca la mejor ruta para una IP destino (longest-prefix match)"""
        return self._lookup_node(self.root, dest_ip)
    
    def _lookup_node(self, node, dest_ip):
        """Método auxiliar para búsqueda de ruta"""
        if not node:
            return None
        
        if self._ip_in_network(dest_ip, node.prefix, node.mask):
            best_match = node
            right_match = self._lookup_node(node.right, dest_ip)
            if right_match:
                return right_match
            return best_match
        
        if dest_ip < node.prefix:
            return self._lookup_node(node.left, dest_ip)
        else:
            return self._lookup_node(node.right, dest_ip)
    
    def _ip_in_network(self, ip, network, mask):
        """Verifica si una IP está en una red dada"""
        ip_parts = [int(x) for x in ip.split('.')]
        net_parts = [int(x) for x in network.split('.')]
        mask_parts = [int(x) for x in mask.split('.')]
        
        for i in range(4):
            if (ip_parts[i] & mask_parts[i]) != (net_parts[i] & mask_parts[i]):
                return False
        return True
    
    def in_order_traversal(self):
        """Recorrido en orden del árbol"""
        routes = []
        self._in_order(self.root, routes)
        return routes
    
    def _in_order(self, node, routes):
        """Método auxiliar para recorrido en orden"""
        if node:
            self._in_order(node.left, routes)
            routes.append(node)
            self._in_order(node.right, routes)
    
    def get_tree_display(self):
        """Retorna representación ASCII del árbol"""
        if not self.root:
            return "Empty tree"
        
        lines = []
        self._build_tree_display(self.root, "", True, lines)
        return "\n".join(lines)
    
    def _build_tree_display(self, node, prefix, is_last, lines):
        """Construye la representación ASCII del árbol"""
        if node:
            node_text = f"[{node.to_cidr()}]"
            lines.append(prefix + node_text)
            
            # Mostrar hijos en formato más simple
            if node.left:
                lines.append(prefix + " /")
                self._build_tree_display(node.left, prefix, False, lines)
            
            if node.right:
                lines.append(prefix + " \\")
                self._build_tree_display(node.right, prefix, False, lines)

class BTreeNode:
    """Nodo para el B-tree de índices persistentes"""
    def __init__(self, is_leaf=False):
        self.keys = []
        self.values = []
        self.children = []
        self.is_leaf = is_leaf
        self.parent = None

class BTree:
    """B-tree para índice persistente de configuraciones"""
    def __init__(self, order=4):
        self.root = BTreeNode(is_leaf=True)
        self.order = order
        self.stats = {
            'height': 1,
            'nodes': 1,
            'splits': 0,
            'merges': 0
        }
    
    def search(self, key):
        """Busca una clave en el B-tree"""
        return self._search_node(self.root, key)
    
    def _search_node(self, node, key):
        """Método auxiliar para búsqueda"""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]
        
        if node.is_leaf:
            return None
        
        return self._search_node(node.children[i], key)
    
    def insert(self, key, value):
        """Inserta una clave-valor en el B-tree"""
        if len(self.root.keys) == (2 * self.order) - 1:
            new_root = BTreeNode()
            new_root.children.append(self.root)
            self.root.parent = new_root
            self._split_child(new_root, 0)
            self.root = new_root
            self.stats['height'] += 1
        
        self._insert_non_full(self.root, key, value)
    
    def _insert_non_full(self, node, key, value):
        """Inserta en un nodo que no está lleno"""
        i = len(node.keys) - 1
        
        if node.is_leaf:
            node.keys.append(None)
            node.values.append(None)
            
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if len(node.children[i].keys) == (2 * self.order) - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)
    
    def _split_child(self, parent, index):
        """Divide un nodo hijo lleno"""
        self.stats['splits'] += 1
        self.stats['nodes'] += 1
        
        full_child = parent.children[index]
        new_child = BTreeNode(is_leaf=full_child.is_leaf)
        
        mid_index = self.order - 1
        
        new_child.keys = full_child.keys[mid_index + 1:]
        new_child.values = full_child.values[mid_index + 1:]
        full_child.keys = full_child.keys[:mid_index]
        full_child.values = full_child.values[:mid_index]
        
        if not full_child.is_leaf:
            new_child.children = full_child.children[mid_index + 1:]
            full_child.children = full_child.children[:mid_index + 1]
            for child in new_child.children:
                child.parent = new_child
        
        parent.children.insert(index + 1, new_child)
        parent.keys.insert(index, full_child.keys[mid_index])
        parent.values.insert(index, full_child.values[mid_index])
        
        new_child.parent = parent
    
    def in_order_traversal(self):
        """Recorrido en orden del B-tree"""
        result = []
        self._in_order(self.root, result)
        return result
    
    def _in_order(self, node, result):
        """Método auxiliar para recorrido en orden"""
        if node:
            for i in range(len(node.keys)):
                if not node.is_leaf:
                    self._in_order(node.children[i], result)
                result.append((node.keys[i], node.values[i]))
            
            if not node.is_leaf:
                self._in_order(node.children[-1], result)

class TrieNode:
    """Nodo para el Trie de prefijos IP"""
    def __init__(self):
        self.children = {}
        self.is_end_of_prefix = False
        self.policies = {}
        self.route_info = None

class Trie:
    """Trie (árbol n-ario) para prefijos IP y políticas jerárquicas"""
    def __init__(self):
        self.root = TrieNode()
    
    def insert_prefix(self, prefix, mask, policies=None):
        """Inserta un prefijo con sus políticas"""
        network_bits = self._prefix_to_bits(prefix, mask)
        node = self.root
        
        for bit in network_bits:
            if bit not in node.children:
                node.children[bit] = TrieNode()
            node = node.children[bit]
        
        node.is_end_of_prefix = True
        if policies:
            node.policies.update(policies)
    
    def _prefix_to_bits(self, prefix, mask):
        """Convierte prefijo e IP a bits de red"""
        ip_parts = [int(x) for x in prefix.split('.')]
        mask_parts = [int(x) for x in mask.split('.')]
        
        bits = []
        for i in range(4):
            network_part = ip_parts[i] & mask_parts[i]
            mask_bits = bin(mask_parts[i]).count('1')
            part_bits = format(network_part, '08b')[:mask_bits]
            bits.extend(part_bits)
        
        return bits
    
    def longest_prefix_match(self, ip):
        """Busca el prefijo más específico para una IP"""
        ip_bits = self._ip_to_bits(ip)
        node = self.root
        last_match = None
        
        for bit in ip_bits:
            if bit in node.children:
                node = node.children[bit]
                if node.is_end_of_prefix:
                    last_match = node
            else:
                break
        
        return last_match
    
    def _ip_to_bits(self, ip):
        """Convierte IP a secuencia de bits"""
        parts = [int(x) for x in ip.split('.')]
        bits = ''
        for part in parts:
            bits += format(part, '08b')
        return bits
    
    def set_policy(self, prefix, mask, policy_type, policy_value):
        """Establece una política para un prefijo"""
        network_bits = self._prefix_to_bits(prefix, mask)
        node = self.root
        
        for bit in network_bits:
            if bit not in node.children:
                node.children[bit] = TrieNode()
            node = node.children[bit]
        
        node.is_end_of_prefix = True
        node.policies[policy_type] = policy_value
    
    def get_inherited_policies(self, ip):
        """Obtiene todas las políticas heredadas para una IP"""
        ip_bits = self._ip_to_bits(ip)
        node = self.root
        policies = {}
        
        for bit in ip_bits:
            if bit in node.children:
                node = node.children[bit]
                if node.is_end_of_prefix:
                    policies.update(node.policies)
            else:
                break
        
        return policies
    
    def display_tree(self):
        """Muestra el árbol de prefijos"""
        result = []
        self._display_node(self.root, "", result, 0)
        if not result:
            return "No prefix policies configured"
        return "\n".join(result)
    
    def _display_node(self, node, current_path, result, depth):
        """Método auxiliar para mostrar el árbol"""
        if node.is_end_of_prefix:
            # Convertir path de bits a formato legible
            prefix_display = self._bits_to_prefix_display(current_path)
            policies_str = ""
            if node.policies:
                policy_list = [f"{k}={v}" for k, v in node.policies.items()]
                policies_str = " {" + ", ".join(policy_list) + "}"
            
            indent = "└── " if depth > 0 else ""
            result.append("  " * max(0, depth - 1) + indent + prefix_display + policies_str)
        
        for bit, child in node.children.items():
            new_path = current_path + bit
            self._display_node(child, new_path, result, depth + 1)
    
    def _bits_to_prefix_display(self, bits):
        """Convierte una secuencia de bits a formato de prefijo legible"""
        if not bits:
            return "0.0.0.0/0"
        
        # Rellenar a múltiplo de 8 si es necesario
        while len(bits) % 8 != 0:
            bits += '0'
        
        # Convertir a octetos
        octets = []
        for i in range(0, min(len(bits), 32), 8):
            octet_bits = bits[i:i+8]
            if len(octet_bits) < 8:
                octet_bits += '0' * (8 - len(octet_bits))
            octets.append(str(int(octet_bits, 2)))
        
        # Rellenar hasta 4 octetos
        while len(octets) < 4:
            octets.append('0')
        
        prefix = '.'.join(octets[:4])
        cidr_len = len([b for b in bits if b == '1'])
        return f"{prefix}/{cidr_len}"

class ErrorLogEntry:
    """Entrada del log de errores"""
    def __init__(self, timestamp, error_type, message, command=None):
        self.timestamp = timestamp
        self.error_type = error_type
        self.message = message
        self.command = command

class ErrorLog:
    """Sistema de registro de errores implementado como cola"""
    def __init__(self):
        self.errors = Queue()
        self.max_entries = 1000
    
    def log_error(self, error_type, message, command=None):
        """Registra un nuevo error"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = ErrorLogEntry(timestamp, error_type, message, command)
        
        if len(self.errors) >= self.max_entries:
            self.errors.dequeue()
        
        self.errors.enqueue(entry)
    
    def get_errors(self, limit=None):
        """Obtiene errores del log"""
        all_errors = self.errors.to_list()
        if limit:
            return all_errors[-limit:]
        return all_errors