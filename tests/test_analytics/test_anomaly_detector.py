"""Tests for AnomalyDetector"""
import pytest
from venom.analytics.anomaly_detector import AnomalyDetector

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def test_zscore_detection():
    """Test Z-score based anomaly detection"""
    detector = AnomalyDetector(method='zscore')
    
    # Create normal data around mean 50
    data = [50.0 + i * 0.5 for i in range(-10, 11)]
    
    detector.fit(data)
    
    assert detector.fitted
    assert detector.mean is not None
    assert detector.std is not None
    
    # Test with normal and anomalous data
    test_data = [50.0, 51.0, 150.0, 49.0, -50.0]  # 150 and -50 are anomalies
    
    anomalies = detector.detect(test_data)
    
    assert len(anomalies) == 5
    assert anomalies[0] == False  # 50.0 is normal
    assert anomalies[1] == False  # 51.0 is normal
    assert anomalies[2] == True   # 150.0 is anomaly
    assert anomalies[3] == False  # 49.0 is normal
    assert anomalies[4] == True   # -50.0 is anomaly


def test_iqr_detection():
    """Test IQR based anomaly detection"""
    detector = AnomalyDetector(method='iqr')
    
    # Create data with known quartiles
    data = list(range(1, 101))  # 1 to 100
    
    detector.fit(data)
    
    assert detector.fitted
    assert detector.q1 is not None
    assert detector.q3 is not None
    assert detector.iqr is not None
    
    # Test with normal and anomalous data
    test_data = [50, 200, -50, 75, 25]  # 200 and -50 should be anomalies
    
    anomalies = detector.detect(test_data)
    
    assert len(anomalies) == 5
    # Middle values should be normal
    assert anomalies[0] == False  # 50 is normal


def test_isolation_forest():
    """Test Isolation Forest anomaly detection"""
    try:
        import sklearn
        detector = AnomalyDetector(method='isolation_forest')
        
        # Create normal data
        data = [[50.0 + i * 0.5] for i in range(-20, 21)]
        
        detector.fit(data)
        
        assert detector.fitted
        
        # Test with normal and anomalous data
        test_data = [[50.0], [51.0], [200.0], [49.0], [-100.0]]
        
        anomalies = detector.detect(test_data)
        
        assert len(anomalies) == 5
        assert isinstance(anomalies[0], bool)
        
    except ImportError:
        pytest.skip("scikit-learn not available")


def test_threshold_setting():
    """Test setting custom threshold"""
    detector = AnomalyDetector(method='zscore')
    
    # Create data
    data = [50.0 + i * 0.5 for i in range(-10, 11)]
    detector.fit(data)
    
    # Get default threshold
    default_threshold = detector.get_threshold()
    assert default_threshold > 0
    
    # Set custom threshold
    new_threshold = 2.0
    detector.set_threshold(new_threshold)
    
    assert detector.get_threshold() == new_threshold
    
    # Test that changing threshold affects detection
    test_data = [50.0, 55.0, 60.0]
    
    # With lower threshold, more anomalies should be detected
    anomalies_low = detector.detect(test_data)
    
    # Set higher threshold
    detector.set_threshold(5.0)
    anomalies_high = detector.detect(test_data)
    
    # Number of anomalies should be different (or at least not more with higher threshold)
    assert sum(anomalies_high) <= sum(anomalies_low)


def test_multidimensional_anomaly():
    """Test anomaly detection on multi-dimensional data"""
    if not HAS_NUMPY:
        pytest.skip("NumPy not available")
    
    import numpy as np
    
    detector = AnomalyDetector(method='zscore')
    
    # Create 2D normal data
    data = []
    for i in range(50):
        data.append([50.0 + i * 0.1, 100.0 + i * 0.2])
    
    data = np.array(data)
    detector.fit(data)
    
    assert detector.fitted
    
    # Test with normal and anomalous data
    test_data = np.array([
        [50.0, 100.0],   # Normal
        [52.0, 102.0],   # Normal
        [200.0, 300.0],  # Anomaly
    ])
    
    anomalies = detector.detect(test_data)
    
    assert len(anomalies) == 3
    assert isinstance(anomalies[0], bool)
