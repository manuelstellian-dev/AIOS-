"""
P2P Mesh Network - Nanobot Phalanx
Enables distributed communication between VENOM nodes

Features:
- FIFO Queue-based message delivery
- Adaptive delay: 0.3ms if queue > 100, else 1ms
- Broadcast to all nanobots except sender
- Direct anomaly and ml_weight injection into genome
"""
import json
import socket
import threading
import time
import queue
from typing import Dict, Any, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class P2PMesh:
    """
    P2P Nanobot Phalanx mesh network for distributed VENOM nodes
    
    Features:
    - FIFO Queue for message management
    - Adaptive delivery delay (0.3ms if qlen > 100, else 1ms)
    - Broadcast capability excluding sender
    """
    
    def __init__(self, node_id: str, host: str = "127.0.0.1", port: int = 0):
        """
        Initialize P2P mesh node (nanobot)
        
        Args:
            node_id: Unique identifier for this nanobot
            host: Host address to bind to
            port: Port to bind to (0 for random available port)
        """
        self.node_id = node_id
        self.host = host
        self.port = port
        
        self.peers: Dict[str, Dict[str, Any]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        
        # FIFO Queue for messages
        self.message_queue: queue.Queue = queue.Queue()
        
        # Adaptive delay thresholds
        self.QUEUE_THRESHOLD = 100
        self.DELAY_HIGH_QUEUE = 0.0003  # 0.3ms
        self.DELAY_LOW_QUEUE = 0.001    # 1ms
        
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.listener_thread: Optional[threading.Thread] = None
        self.delivery_thread: Optional[threading.Thread] = None
        
    def start(self):
        """Start the P2P mesh nanobot"""
        if self.running:
            return
            
        # Create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        
        # Get actual port if random was used
        if self.port == 0:
            self.port = self.socket.getsockname()[1]
            
        self.socket.listen(5)
        self.running = True
        
        # Start listener thread
        self.listener_thread = threading.Thread(target=self._listen_for_connections, daemon=True)
        self.listener_thread.start()
        
        # Start adaptive delivery thread
        self.delivery_thread = threading.Thread(target=self._adaptive_delivery, daemon=True)
        self.delivery_thread.start()
        
        logger.info(f"P2P nanobot {self.node_id} started on {self.host}:{self.port}")
        
    def stop(self):
        """Stop the P2P mesh nanobot"""
        if not self.running:
            return
            
        self.running = False
        
        if self.socket:
            self.socket.close()
            
        if self.listener_thread:
            self.listener_thread.join(timeout=1.0)
            
        if self.delivery_thread:
            self.delivery_thread.join(timeout=1.0)
            
        logger.info(f"P2P nanobot {self.node_id} stopped")
    
    def _adaptive_delivery(self):
        """
        Adaptive delivery daemon thread
        Delivers messages from queue with adaptive delay based on queue length
        """
        while self.running:
            try:
                # Check queue length for adaptive delay
                qlen = self.message_queue.qsize()
                
                # Adaptive delay: 0.3ms if qlen > 100, else 1ms
                if qlen > self.QUEUE_THRESHOLD:
                    delay = self.DELAY_HIGH_QUEUE
                else:
                    delay = self.DELAY_LOW_QUEUE
                
                # Try to get message with timeout
                try:
                    message = self.message_queue.get(timeout=delay)
                    self._deliver_message(message)
                    self.message_queue.task_done()
                except queue.Empty:
                    pass
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Error in adaptive delivery: {e}")
    
    def _deliver_message(self, message: Dict[str, Any]):
        """Deliver a single message (process handlers)"""
        msg_type = message.get("type")
        if msg_type in self.message_handlers:
            try:
                handler = self.message_handlers[msg_type]
                handler(message)
            except Exception as e:
                logger.error(f"Error in message handler for {msg_type}: {e}")
        
    def _listen_for_connections(self):
        """Listen for incoming connections"""
        while self.running:
            try:
                if not self.socket:
                    break
                    
                self.socket.settimeout(1.0)
                try:
                    client_socket, address = self.socket.accept()
                except socket.timeout:
                    continue
                    
                # Handle connection in separate thread
                thread = threading.Thread(
                    target=self._handle_connection,
                    args=(client_socket, address),
                    daemon=True
                )
                thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error in listener: {e}")
                    
    def _handle_connection(self, client_socket: socket.socket, address: tuple):
        """Handle an incoming connection"""
        try:
            # Receive data
            data = client_socket.recv(4096)
            if not data:
                return
                
            message = json.loads(data.decode())
            
            # Process message
            self._process_message(message, address)
            
            # Send acknowledgment
            response = {"status": "ok", "node_id": self.node_id}
            client_socket.send(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"Error handling connection from {address}: {e}")
        finally:
            client_socket.close()
            
    def _process_message(self, message: Dict[str, Any], sender_address: tuple):
        """Process received message and add to queue"""
        msg_type = message.get("type")
        
        if msg_type == "peer_discovery":
            # Register peer
            peer_id = message.get("node_id")
            if peer_id and peer_id != self.node_id:
                self.peers[peer_id] = {
                    "node_id": peer_id,
                    "address": sender_address,
                    "last_seen": time.time(),
                    "data": message.get("data", {})
                }
                logger.info(f"Nanobot peer {peer_id} discovered")
        else:
            # Add message to queue for adaptive delivery
            self.message_queue.put(message)
                
    def register_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for a specific message type
        
        Args:
            message_type: Type of message to handle
            handler: Callable to handle the message
        """
        self.message_handlers[message_type] = handler
        
    def send_to_peer(self, peer_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to a specific peer
        
        Args:
            peer_id: Target peer ID
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if peer_id not in self.peers:
            logger.warning(f"Peer {peer_id} not found")
            return False
            
        peer = self.peers[peer_id]
        address = peer["address"]
        
        try:
            # Create connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5.0)
            client_socket.connect(address)
            
            # Send message
            message["sender_id"] = self.node_id
            client_socket.send(json.dumps(message).encode())
            
            # Receive response
            response = client_socket.recv(4096)
            client_socket.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending to peer {peer_id}: {e}")
            return False
            
    def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast message to all nanobots except sender
        
        Args:
            message: Message to broadcast
        """
        message["sender_id"] = self.node_id
        
        # Broadcast to all peers except self
        for peer_id in list(self.peers.keys()):
            if peer_id != self.node_id:
                self.send_to_peer(peer_id, message)
    
    def inject_data(self, genome: Dict[str, Any], anoms: Optional[int] = None, 
                    ml_weight: Optional[float] = None):
        """
        Inject anomalies or ML weight directly into genome
        Simulates distributed risk injection
        
        Args:
            genome: Genome dictionary to update
            anoms: Number of anomalies to inject
            ml_weight: ML weight to inject
        """
        if anoms is not None:
            if "risk" not in genome:
                genome["risk"] = {}
            genome["risk"]["anoms"] = genome["risk"].get("anoms", 0) + anoms
            logger.debug(f"Injected {anoms} anomalies into genome")
        
        if ml_weight is not None:
            if "ml" not in genome:
                genome["ml"] = {}
            genome["ml"]["ml_weight"] = ml_weight
            logger.debug(f"Injected ml_weight {ml_weight} into genome")
            
    def discover_peer(self, host: str, port: int, peer_data: Optional[Dict[str, Any]] = None):
        """
        Discover and connect to a peer
        
        Args:
            host: Peer host address
            port: Peer port
            peer_data: Optional data to send with discovery
        """
        try:
            message = {
                "type": "peer_discovery",
                "node_id": self.node_id,
                "data": peer_data or {}
            }
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5.0)
            client_socket.connect((host, port))
            
            client_socket.send(json.dumps(message).encode())
            response = client_socket.recv(4096)
            client_socket.close()
            
            if response:
                resp_data = json.loads(response.decode())
                peer_id = resp_data.get("node_id")
                if peer_id:
                    self.peers[peer_id] = {
                        "node_id": peer_id,
                        "address": (host, port),
                        "last_seen": time.time(),
                        "data": {}
                    }
                    logger.info(f"Connected to peer {peer_id}")
                    
        except Exception as e:
            logger.error(f"Error discovering peer at {host}:{port}: {e}")
            
    def get_peers(self) -> List[Dict[str, Any]]:
        """Get list of connected peers"""
        return list(self.peers.values())
    
    def get_peer_count(self) -> int:
        """Get number of connected peers"""
        return len(self.peers)
