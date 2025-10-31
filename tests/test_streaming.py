"""Test Stream Analytics"""
import pytest
from venom.analytics.streaming import StreamProcessor

def test_stream_processor_init():
    """Test stream processor initializes correctly"""
    processor = StreamProcessor(window_size=50, anomaly_threshold=3.0)
    assert processor is not None
    assert processor.window_size == 50
    assert processor.anomaly_threshold == 3.0
    assert processor.total_processed == 0
    assert processor.anomalies_detected == 0

def test_stream_processor_ingest():
    """Test basic data ingestion"""
    processor = StreamProcessor(window_size=10)
    
    # Ingest normal values
    for i in range(5):
        result = processor.ingest(10.0 + i)
        # No anomaly for normal values
        assert result == False
    
    assert processor.total_processed == 5

def test_stream_processor_anomaly_detection():
    """Test Z-score anomaly detection"""
    processor = StreamProcessor(window_size=20, anomaly_threshold=3.0)
    
    # Ingest normal values around 50
    for i in range(10):
        processor.ingest(50.0 + i * 0.5)
    
    # Ingest a clear anomaly (far from mean)
    anomaly_detected = processor.ingest(150.0)
    
    assert anomaly_detected == True
    assert processor.anomalies_detected == 1

def test_stream_processor_handler_callback():
    """Test anomaly handler callbacks are triggered"""
    processor = StreamProcessor(window_size=20, anomaly_threshold=3.0)
    
    detected_values = []
    
    def anomaly_handler(value):
        detected_values.append(value)
    
    processor.register_handler(anomaly_handler)
    
    # Ingest normal values
    for i in range(10):
        processor.ingest(100.0 + i)
    
    # Ingest anomaly
    processor.ingest(200.0)
    
    assert len(detected_values) > 0
    assert 200.0 in detected_values

def test_stream_processor_rolling_window_stats():
    """Test rolling window statistics"""
    processor = StreamProcessor(window_size=5)
    
    # Ingest values: 10, 20, 30, 40, 50
    for i in range(1, 6):
        processor.ingest(i * 10.0)
    
    stats = processor.get_stats()
    
    assert stats["count"] == 5
    assert stats["mean"] == 30.0
    assert stats["min"] == 10.0
    assert stats["max"] == 50.0
    assert stats["total_processed"] == 5
    assert "stdev" in stats

def test_stream_processor_window_limit():
    """Test rolling window respects size limit"""
    processor = StreamProcessor(window_size=3)
    
    # Ingest 5 values
    for i in range(5):
        processor.ingest(i * 10.0)
    
    stats = processor.get_stats()
    
    # Window should only contain last 3 values
    assert stats["count"] == 3
    assert stats["total_processed"] == 5
    assert stats["min"] == 20.0  # Values: 20, 30, 40
    assert stats["max"] == 40.0
