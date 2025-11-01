"""
VENOM Anomaly Detector - Multi-algorithm anomaly detection
Provides Z-score, IQR, and Isolation Forest based anomaly detection
"""

import logging
from typing import Optional
import statistics

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("NumPy not available, using fallback methods")

try:
    from sklearn.ensemble import IsolationForest as SklearnIsolationForest
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("scikit-learn not available, Isolation Forest disabled")


class AnomalyDetector:
    """
    Multi-algorithm anomaly detector
    Supports Z-score, IQR, and Isolation Forest methods
    """
    
    def __init__(self, method: str = 'zscore'):
        """
        Initialize anomaly detector
        
        Args:
            method: Detection method ('zscore', 'iqr', 'isolation_forest')
        """
        valid_methods = ['zscore', 'iqr', 'isolation_forest']
        if method not in valid_methods:
            raise ValueError(f"method must be one of {valid_methods}, got '{method}'")
        
        self.method = method
        self.fitted = False
        self.threshold: Optional[float] = None
        
        # Statistics for zscore and iqr methods
        self.mean: Optional[float] = None
        self.std: Optional[float] = None
        self.q1: Optional[float] = None
        self.q3: Optional[float] = None
        self.iqr: Optional[float] = None
        
        # Isolation Forest model
        self.isolation_forest = None
        
        logger.info(f"AnomalyDetector initialized with method='{method}'")
    
    def fit(self, data) -> None:
        """
        Fit the detector on training data
        
        Args:
            data: Training data (numpy array or list)
        """
        if HAS_NUMPY:
            if not isinstance(data, np.ndarray):
                data = np.array(data)
            
            if data.ndim == 1:
                data = data.reshape(-1, 1)
        else:
            # Convert to list of lists for consistency
            if isinstance(data, list) and len(data) > 0 and not isinstance(data[0], list):
                data = [[x] for x in data]
        
        if self.method == 'zscore':
            self._fit_zscore(data)
        elif self.method == 'iqr':
            self._fit_iqr(data)
        elif self.method == 'isolation_forest':
            self._fit_isolation_forest(data)
        
        self.fitted = True
        logger.info(f"Fitted on {len(data)} samples")
    
    def _fit_zscore(self, data) -> None:
        """Fit Z-score method"""
        if HAS_NUMPY:
            # For multi-dimensional data, compute mean and std per feature
            if data.ndim == 2 and data.shape[1] > 1:
                self.mean = np.mean(data, axis=0)
                self.std = np.std(data, axis=0)
            else:
                values = data.flatten()
                self.mean = float(np.mean(values))
                self.std = float(np.std(values))
        else:
            values = [x[0] if isinstance(x, list) else x for x in data]
            self.mean = statistics.mean(values)
            self.std = statistics.stdev(values) if len(values) > 1 else 0.0
        
        # Default threshold: 3 standard deviations
        if self.threshold is None:
            self.threshold = 3.0
    
    def _fit_iqr(self, data) -> None:
        """Fit IQR method"""
        if HAS_NUMPY:
            values = data.flatten()
            self.q1 = float(np.percentile(values, 25))
            self.q3 = float(np.percentile(values, 75))
        else:
            values = sorted([x[0] if isinstance(x, list) else x for x in data])
            n = len(values)
            self.q1 = values[n // 4]
            self.q3 = values[3 * n // 4]
        
        self.iqr = self.q3 - self.q1
        
        # Default threshold: 1.5 * IQR
        if self.threshold is None:
            self.threshold = 1.5
    
    def _fit_isolation_forest(self, data) -> None:
        """Fit Isolation Forest"""
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not available, falling back to Z-score method")
            self.method = 'zscore'
            self._fit_zscore(data)
            return
        
        if not HAS_NUMPY:
            logger.warning("NumPy not available, falling back to Z-score method")
            self.method = 'zscore'
            self._fit_zscore(data)
            return
        
        # Ensure data is 2D numpy array
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        self.isolation_forest = SklearnIsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.isolation_forest.fit(data)
        
        # Calculate threshold based on scores
        scores = -self.isolation_forest.score_samples(data)
        if self.threshold is None:
            self.threshold = float(np.percentile(scores, 99))
    
    def detect(self, data) -> list:
        """
        Detect anomalies in data
        
        Args:
            data: Data to check for anomalies (numpy array or list)
            
        Returns:
            Boolean mask (list or numpy array) indicating anomalies
        """
        if not self.fitted:
            raise RuntimeError("Must call fit() before detect()")
        
        if HAS_NUMPY:
            if not isinstance(data, np.ndarray):
                data = np.array(data)
            
            if data.ndim == 1:
                data = data.reshape(-1, 1)
        else:
            # Convert to list of lists for consistency
            if isinstance(data, list) and len(data) > 0 and not isinstance(data[0], list):
                data = [[x] for x in data]
        
        scores = self.score(data)
        
        if HAS_NUMPY and isinstance(scores, np.ndarray):
            return (scores > self.threshold).tolist()
        else:
            return [s > self.threshold for s in scores]
    
    def score(self, data) -> list:
        """
        Calculate anomaly scores
        
        Args:
            data: Data to score (numpy array or list)
            
        Returns:
            Anomaly scores (higher = more anomalous)
        """
        if not self.fitted:
            raise RuntimeError("Must call fit() before score()")
        
        if HAS_NUMPY:
            if not isinstance(data, np.ndarray):
                data = np.array(data)
            
            if data.ndim == 1:
                data = data.reshape(-1, 1)
        else:
            # Convert to list of lists for consistency
            if isinstance(data, list) and len(data) > 0 and not isinstance(data[0], list):
                data = [[x] for x in data]
        
        if self.method == 'zscore':
            return self._score_zscore(data)
        elif self.method == 'iqr':
            return self._score_iqr(data)
        elif self.method == 'isolation_forest':
            return self._score_isolation_forest(data)
    
    def _score_zscore(self, data) -> list:
        """Calculate Z-score based anomaly scores"""
        if HAS_NUMPY:
            # For multi-dimensional data, calculate scores per sample
            if data.ndim == 2 and data.shape[1] > 1:
                # Calculate distance from mean in multi-dimensional space
                # Use Mahalanobis-like distance (simplified)
                centered = data - self.mean
                # Check if std is array or scalar
                if isinstance(self.std, np.ndarray):
                    std_check = np.all(self.std == 0)
                else:
                    std_check = (self.std == 0)
                
                if std_check:
                    return [0.0] * len(data)
                
                z_scores = np.sqrt(np.sum((centered / self.std) ** 2, axis=1))
                return z_scores.tolist()
            else:
                # For 1D data
                values = data.flatten()
                if self.std == 0:
                    return [0.0] * len(values)
                scores = np.abs((values - self.mean) / self.std)
                return scores.tolist()
        else:
            values = [x[0] if isinstance(x, list) else x for x in data]
            if self.std == 0:
                return [0.0] * len(values)
            return [abs((v - self.mean) / self.std) for v in values]
    
    def _score_iqr(self, data) -> list:
        """Calculate IQR based anomaly scores"""
        if HAS_NUMPY:
            values = data.flatten()
            lower_bound = self.q1 - self.threshold * self.iqr
            upper_bound = self.q3 + self.threshold * self.iqr
            
            # Score is distance from bounds (0 if within bounds)
            scores = np.maximum(
                np.maximum(lower_bound - values, values - upper_bound),
                0
            )
            return scores.tolist()
        else:
            values = [x[0] if isinstance(x, list) else x for x in data]
            lower_bound = self.q1 - self.threshold * self.iqr
            upper_bound = self.q3 + self.threshold * self.iqr
            
            scores = []
            for v in values:
                if v < lower_bound:
                    scores.append(lower_bound - v)
                elif v > upper_bound:
                    scores.append(v - upper_bound)
                else:
                    scores.append(0.0)
            return scores
    
    def _score_isolation_forest(self, data) -> list:
        """Calculate Isolation Forest anomaly scores"""
        if self.isolation_forest is None:
            logger.warning("Isolation Forest not available, using Z-score fallback")
            return self._score_zscore(data)
        
        if not HAS_NUMPY:
            logger.warning("NumPy not available, using Z-score fallback")
            return self._score_zscore(data)
        
        # Ensure data is 2D numpy array
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        # Negative score_samples gives anomaly scores (higher = more anomalous)
        scores = -self.isolation_forest.score_samples(data)
        return scores.tolist()
    
    def get_threshold(self) -> float:
        """Get current threshold"""
        return self.threshold if self.threshold is not None else 0.0
    
    def set_threshold(self, threshold: float) -> None:
        """
        Set detection threshold
        
        Args:
            threshold: New threshold value
        """
        self.threshold = threshold
        logger.info(f"Threshold set to {threshold}")
