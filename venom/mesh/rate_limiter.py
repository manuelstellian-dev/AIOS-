"""Rate limiting for mesh using token bucket."""
import time
import threading
from typing import Optional, Dict

class TokenBucket:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket.
        
        Args:
            rate: Tokens per second
            capacity: Max bucket capacity
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens.
        
        Returns:
            True if tokens consumed, False if rate limited
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now
            
            # Add tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_tokens(self) -> float:
        """Get current token count."""
        with self.lock:
            return self.tokens

class MeshRateLimiter:
    """Rate limiter for P2P mesh."""
    
    def __init__(self, rate_per_node: float = 100, rate_per_topic: float = 50):
        """
        Initialize mesh rate limiter.
        
        Args:
            rate_per_node: Max messages per second per node
            rate_per_topic: Max messages per second per topic
        """
        self.rate_per_node = rate_per_node
        self.rate_per_topic = rate_per_topic
        self.node_limiters = {}
        self.topic_limiters = {}
        self.blocked_count = 0
    
    def check_node_limit(self, node_id: str) -> bool:
        """Check if node is rate limited."""
        if node_id not in self.node_limiters:
            self.node_limiters[node_id] = TokenBucket(self.rate_per_node, int(self.rate_per_node * 2))
        
        allowed = self.node_limiters[node_id].consume()
        if not allowed:
            self.blocked_count += 1
        return allowed
    
    def check_topic_limit(self, topic: str) -> bool:
        """Check if topic is rate limited."""
        if topic not in self.topic_limiters:
            self.topic_limiters[topic] = TokenBucket(self.rate_per_topic, int(self.rate_per_topic * 2))
        
        allowed = self.topic_limiters[topic].consume()
        if not allowed:
            self.blocked_count += 1
        return allowed
    
    def check_limits(self, node_id: str, topic: str) -> bool:
        """Check both node and topic limits."""
        return self.check_node_limit(node_id) and self.check_topic_limit(topic)
    
    def get_stats(self) -> Dict[str, int]:
        """Get rate limiter statistics."""
        return {
            'node_count': len(self.node_limiters),
            'topic_count': len(self.topic_limiters),
            'blocked_total': self.blocked_count
        }
