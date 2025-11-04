"""
Comprehensive tests for venom/mesh/rate_limiter.py
Tests token bucket rate limiting and mesh rate limiting
"""
import pytest
import time
from venom.mesh.rate_limiter import TokenBucket, MeshRateLimiter


class TestTokenBucket:
    """Tests for TokenBucket class"""
    
    def test_init(self):
        """Test TokenBucket initialization"""
        bucket = TokenBucket(rate=10.0, capacity=100)
        assert bucket.rate == 10.0
        assert bucket.capacity == 100
        assert bucket.tokens == 100  # Starts full
    
    def test_consume_success(self):
        """Test successful token consumption"""
        bucket = TokenBucket(rate=10.0, capacity=100)
        assert bucket.consume(10) is True
        assert bucket.tokens == 90
    
    def test_consume_insufficient_tokens(self):
        """Test consumption when not enough tokens"""
        bucket = TokenBucket(rate=1.0, capacity=5)
        bucket.tokens = 2
        assert bucket.consume(3) is False
        # Tokens may have been refilled slightly due to time elapsed
        assert bucket.tokens >= 2  # Should not have consumed (at least 2 left)
    
    def test_token_refill(self):
        """Test tokens refill over time"""
        bucket = TokenBucket(rate=10.0, capacity=100)
        bucket.tokens = 50
        time.sleep(0.1)  # Wait 0.1 seconds
        bucket.consume(1)  # Trigger refill
        # Should have refilled ~1 token (10 * 0.1 = 1)
        assert bucket.tokens > 49  # At least 49 remaining after consuming 1
    
    def test_get_tokens(self):
        """Test get_tokens method"""
        bucket = TokenBucket(rate=10.0, capacity=100)
        assert bucket.get_tokens() == 100
        bucket.consume(20)
        assert bucket.get_tokens() == 80


class TestMeshRateLimiter:
    """Tests for MeshRateLimiter class"""
    
    def test_init(self):
        """Test MeshRateLimiter initialization"""
        limiter = MeshRateLimiter(rate_per_node=100, rate_per_topic=50)
        assert limiter.rate_per_node == 100
        assert limiter.rate_per_topic == 50
        assert limiter.blocked_count == 0
    
    def test_check_node_limit_allowed(self):
        """Test node limit when under limit"""
        limiter = MeshRateLimiter(rate_per_node=1000)
        assert limiter.check_node_limit("node1") is True
        assert limiter.blocked_count == 0
    
    def test_check_node_limit_blocked(self):
        """Test node limit when over limit"""
        limiter = MeshRateLimiter(rate_per_node=1)
        # Consume all tokens
        for _ in range(10):
            limiter.check_node_limit("node1")
        # Should be blocked now
        assert limiter.check_node_limit("node1") is False
        assert limiter.blocked_count > 0
    
    def test_check_topic_limit_allowed(self):
        """Test topic limit when under limit"""
        limiter = MeshRateLimiter(rate_per_topic=1000)
        assert limiter.check_topic_limit("topic1") is True
        assert limiter.blocked_count == 0
    
    def test_check_topic_limit_blocked(self):
        """Test topic limit when over limit"""
        limiter = MeshRateLimiter(rate_per_topic=1)
        # Consume all tokens
        for _ in range(10):
            limiter.check_topic_limit("topic1")
        # Should be blocked now
        assert limiter.check_topic_limit("topic1") is False
        assert limiter.blocked_count > 0
    
    def test_check_limits_both_allowed(self):
        """Test checking both node and topic limits when allowed"""
        limiter = MeshRateLimiter(rate_per_node=1000, rate_per_topic=1000)
        assert limiter.check_limits("node1", "topic1") is True
    
    def test_check_limits_node_blocked(self):
        """Test checking limits when node is blocked"""
        limiter = MeshRateLimiter(rate_per_node=1, rate_per_topic=1000)
        # Exhaust node tokens
        for _ in range(10):
            limiter.check_node_limit("node1")
        # Both checks should fail because node is blocked
        assert limiter.check_limits("node1", "topic1") is False
    
    def test_check_limits_topic_blocked(self):
        """Test checking limits when topic is blocked"""
        limiter = MeshRateLimiter(rate_per_node=1000, rate_per_topic=1)
        # Exhaust topic tokens
        for _ in range(10):
            limiter.check_topic_limit("topic1")
        # Both checks should fail because topic is blocked
        assert limiter.check_limits("node1", "topic1") is False
    
    def test_get_stats(self):
        """Test getting rate limiter statistics"""
        limiter = MeshRateLimiter()
        stats = limiter.get_stats()
        assert stats['node_count'] == 0
        assert stats['topic_count'] == 0
        assert stats['blocked_total'] == 0
        
        # Add some activity
        limiter.check_node_limit("node1")
        limiter.check_node_limit("node2")
        limiter.check_topic_limit("topic1")
        
        stats = limiter.get_stats()
        assert stats['node_count'] == 2
        assert stats['topic_count'] == 1
    
    def test_multiple_nodes(self):
        """Test rate limiting with multiple nodes"""
        limiter = MeshRateLimiter(rate_per_node=100)
        # Different nodes should have separate limits
        assert limiter.check_node_limit("node1") is True
        assert limiter.check_node_limit("node2") is True
        assert limiter.check_node_limit("node3") is True
        assert len(limiter.node_limiters) == 3
    
    def test_multiple_topics(self):
        """Test rate limiting with multiple topics"""
        limiter = MeshRateLimiter(rate_per_topic=100)
        # Different topics should have separate limits
        assert limiter.check_topic_limit("topic1") is True
        assert limiter.check_topic_limit("topic2") is True
        assert limiter.check_topic_limit("topic3") is True
        assert len(limiter.topic_limiters) == 3
