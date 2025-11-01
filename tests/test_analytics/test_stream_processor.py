"""Tests for StreamProcessor"""
import pytest
from venom.analytics.stream_processor import StreamProcessor


def test_add_event():
    """Test adding events to stream processor"""
    processor = StreamProcessor(window_size=10, window_type='sliding')
    
    # Add some events
    for i in range(5):
        event = {'value': i * 10, 'label': f'event_{i}'}
        processor.add_event(event)
    
    assert processor.total_events == 5
    window = processor.get_window()
    assert len(window) == 5
    
    # Check that timestamps were added
    for event in window:
        assert 'timestamp' in event


def test_sliding_window():
    """Test sliding window behavior"""
    processor = StreamProcessor(window_size=3, window_type='sliding')
    
    # Add more events than window size
    for i in range(5):
        event = {'value': i}
        processor.add_event(event)
    
    # Window should only contain last 3 events
    window = processor.get_window()
    assert len(window) == 3
    assert window[0]['value'] == 2
    assert window[1]['value'] == 3
    assert window[2]['value'] == 4


def test_aggregate():
    """Test aggregation functions"""
    processor = StreamProcessor(window_size=10, window_type='sliding')
    
    # Add events with values
    for i in range(5):
        event = {'value': (i + 1) * 10}  # 10, 20, 30, 40, 50
        processor.add_event(event)
    
    # Test different aggregations
    assert processor.aggregate('value', 'mean') == 30.0
    assert processor.aggregate('value', 'sum') == 150.0
    assert processor.aggregate('value', 'count') == 5.0
    assert processor.aggregate('value', 'min') == 10.0
    assert processor.aggregate('value', 'max') == 50.0
    
    # Test standard deviation
    std = processor.aggregate('value', 'std')
    assert std > 0  # Should have some variance


def test_filter():
    """Test filtering events"""
    processor = StreamProcessor(window_size=10, window_type='sliding')
    
    # Add events with different labels
    for i in range(10):
        event = {'value': i, 'type': 'even' if i % 2 == 0 else 'odd'}
        processor.add_event(event)
    
    # Filter for even events
    even_events = processor.filter(lambda e: e.get('type') == 'even')
    assert len(even_events) == 5
    
    # Filter for values > 5
    high_value_events = processor.filter(lambda e: e.get('value', 0) > 5)
    assert len(high_value_events) == 4


def test_compute_statistics():
    """Test computing stream statistics"""
    processor = StreamProcessor(window_size=10, window_type='sliding')
    
    # Add some events
    for i in range(5):
        event = {'value': i}
        processor.add_event(event)
    
    stats = processor.compute_statistics()
    
    # Check that statistics are present
    assert 'total_events' in stats
    assert stats['total_events'] == 5.0
    assert 'window_size' in stats
    assert stats['window_size'] == 5.0
    assert 'throughput' in stats
    assert stats['throughput'] > 0  # Should have some throughput
    assert 'elapsed_time' in stats
