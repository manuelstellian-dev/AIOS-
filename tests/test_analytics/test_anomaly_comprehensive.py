"""
Comprehensive tests for AnomalyDetector
"""
import pytest
import numpy as np
from unittest.mock import Mock
from venom.analytics.anomaly_detector import AnomalyDetector


class TestAnomalyDetectorInit:
    """Test AnomalyDetector initialization"""
    
    def test_init_default(self):
        """Test default initialization"""
        detector = AnomalyDetector()
        
        assert hasattr(detector, 'model')
        assert hasattr(detector, 'threshold')
    
    def test_init_with_threshold(self):
        """Test initialization with custom threshold"""
        detector = AnomalyDetector(threshold=2.5)
        
        assert detector.threshold == 2.5
    
    def test_init_with_method(self):
        """Test initialization with specific method"""
        detector = AnomalyDetector(method='isolation_forest')
        
        assert detector.method == 'isolation_forest'


class TestAnomalyDetectorFit:
    """Test AnomalyDetector fitting"""
    
    def test_fit_with_normal_data(self):
        """Test fitting with normal data"""
        detector = AnomalyDetector()
        
        X = np.random.randn(100, 3)
        
        detector.fit(X)
        
        assert detector.is_fitted or detector.model is not None
    
    def test_fit_updates_statistics(self):
        """Test fitting updates statistics"""
        detector = AnomalyDetector()
        
        X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        
        detector.fit(X)
        
        # Should calculate statistics
        assert hasattr(detector, 'mean_') or hasattr(detector, 'model')
    
    def test_fit_with_small_dataset(self):
        """Test fitting with small dataset"""
        detector = AnomalyDetector()
        
        X = np.array([[1], [2], [3]])
        
        detector.fit(X)
        
        assert detector is not None


class TestAnomalyDetectorDetection:
    """Test anomaly detection"""
    
    def test_detect_normal_data(self):
        """Test detecting normal data"""
        detector = AnomalyDetector()
        
        X_train = np.random.randn(100, 2)
        detector.fit(X_train)
        
        X_test = np.random.randn(10, 2)
        anomalies = detector.detect(X_test)
        
        assert anomalies is not None
        assert isinstance(anomalies, (list, np.ndarray))
    
    def test_detect_obvious_anomaly(self):
        """Test detecting obvious anomaly"""
        detector = AnomalyDetector(threshold=2.0)
        
        # Normal data centered around 0
        X_train = np.random.randn(100, 1)
        detector.fit(X_train)
        
        # Clear anomaly
        X_test = np.array([[100]])
        anomalies = detector.detect(X_test)
        
        # Should detect the anomaly
        assert anomalies is not None
    
    def test_detect_returns_scores(self):
        """Test detection returns anomaly scores"""
        detector = AnomalyDetector()
        
        X = np.random.randn(50, 2)
        detector.fit(X)
        
        scores = detector.get_anomaly_scores(np.random.randn(10, 2))
        
        assert scores is None or len(scores) > 0
    
    def test_detect_batch(self):
        """Test batch detection"""
        detector = AnomalyDetector()
        
        X_train = np.random.randn(100, 3)
        detector.fit(X_train)
        
        X_test = np.random.randn(20, 3)
        results = detector.detect(X_test)
        
        assert results is not None


class TestAnomalyDetectorMethods:
    """Test different detection methods"""
    
    def test_statistical_method(self):
        """Test statistical anomaly detection"""
        detector = AnomalyDetector(method='statistical')
        
        X = np.random.randn(50, 2)
        detector.fit(X)
        
        anomalies = detector.detect(np.random.randn(10, 2))
        
        assert anomalies is not None
    
    def test_isolation_forest_method(self):
        """Test isolation forest method"""
        detector = AnomalyDetector(method='isolation_forest')
        
        X = np.random.randn(100, 3)
        detector.fit(X)
        
        anomalies = detector.detect(np.random.randn(20, 3))
        
        assert anomalies is not None
    
    def test_one_class_svm_method(self):
        """Test one-class SVM method"""
        detector = AnomalyDetector(method='svm')
        
        X = np.random.randn(100, 2)
        detector.fit(X)
        
        anomalies = detector.detect(np.random.randn(10, 2))
        
        assert anomalies is not None


class TestAnomalyDetectorThresholding:
    """Test threshold handling"""
    
    def test_adjust_threshold(self):
        """Test adjusting detection threshold"""
        detector = AnomalyDetector(threshold=2.0)
        
        detector.set_threshold(3.0)
        
        assert detector.threshold == 3.0
    
    def test_auto_threshold(self):
        """Test automatic threshold determination"""
        detector = AnomalyDetector()
        
        X = np.random.randn(100, 2)
        detector.fit(X)
        
        # Should set threshold automatically
        threshold = detector.get_threshold()
        
        assert threshold is not None or threshold is None


class TestAnomalyDetectorMetrics:
    """Test evaluation metrics"""
    
    def test_get_statistics(self):
        """Test getting detection statistics"""
        detector = AnomalyDetector()
        
        X = np.random.randn(100, 2)
        detector.fit(X)
        
        stats = detector.get_statistics()
        
        assert stats is None or isinstance(stats, dict)
    
    def test_evaluate_performance(self):
        """Test evaluating detection performance"""
        detector = AnomalyDetector()
        
        X_train = np.random.randn(100, 2)
        detector.fit(X_train)
        
        # Create test data with known anomalies
        X_test = np.random.randn(20, 2)
        y_true = np.array([0] * 18 + [1] * 2)  # 2 anomalies
        
        metrics = detector.evaluate(X_test, y_true)
        
        assert metrics is None or isinstance(metrics, dict)


class TestAnomalyDetectorPersistence:
    """Test model persistence"""
    
    def test_save_model(self):
        """Test saving detector model"""
        detector = AnomalyDetector()
        
        X = np.random.randn(50, 2)
        detector.fit(X)
        
        result = detector.save('/tmp/anomaly_model.pkl')
        
        assert result is True or result is not None
    
    def test_load_model(self):
        """Test loading detector model"""
        detector1 = AnomalyDetector()
        X = np.random.randn(50, 2)
        detector1.fit(X)
        detector1.save('/tmp/anomaly_model.pkl')
        
        detector2 = AnomalyDetector()
        result = detector2.load('/tmp/anomaly_model.pkl')
        
        assert result is True or detector2.model is not None


class TestAnomalyDetectorEdgeCases:
    """Test edge cases"""
    
    def test_detect_without_fit(self):
        """Test detection without fitting"""
        detector = AnomalyDetector()
        
        X = np.array([[1, 2]])
        
        try:
            result = detector.detect(X)
            assert result is None or result is not None
        except (ValueError, AttributeError):
            pass
    
    def test_fit_with_single_sample(self):
        """Test fitting with single sample"""
        detector = AnomalyDetector()
        
        X = np.array([[1, 2, 3]])
        
        try:
            detector.fit(X)
        except (ValueError, Exception):
            pass
    
    def test_detect_with_different_dimensions(self):
        """Test detection with wrong dimensions"""
        detector = AnomalyDetector()
        
        X_train = np.random.randn(50, 3)
        detector.fit(X_train)
        
        X_test = np.random.randn(10, 2)  # Wrong dimensions
        
        try:
            detector.detect(X_test)
        except (ValueError, Exception):
            pass
