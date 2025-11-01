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
    
    def __init__(self, method: str = 'zscore', threshold: Optional[float] = None):
        """
        Initialize anomaly detector
        
        Args:
            method: Detection method ('zscore', 'iqr', 'isolation_forest', 'statistical', 'svm')
            threshold: Optional custom threshold for anomaly detection
        """
        # Map method aliases
        method_map = {
            'statistical': 'zscore',
            'svm': 'one_class_svm'
        }
        method = method_map.get(method, method)
        
        valid_methods = ['zscore', 'iqr', 'isolation_forest', 'one_class_svm']
        if method not in valid_methods:
            raise ValueError(f"method must be one of {valid_methods}, got '{method}'")
        
        self.method = method
        self.fitted = False
        self.is_fitted = False  # Alias for compatibility
        self.threshold: Optional[float] = threshold
        
        # Statistics for zscore and iqr methods
        self.mean: Optional[float] = None
        self.mean_: Optional[float] = None  # Scikit-learn style attribute
        self.std: Optional[float] = None
        self.q1: Optional[float] = None
        self.q3: Optional[float] = None
        self.iqr: Optional[float] = None
        
        # Model attribute for compatibility
        self.model = None
        
        # Isolation Forest model
        self.isolation_forest = None
        
        # One-class SVM model
        self.one_class_svm = None
        
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
        elif self.method == 'one_class_svm':
            self._fit_one_class_svm(data)
        
        self.fitted = True
        self.is_fitted = True
        
        # Set mean_ for compatibility
        if self.mean is not None:
            self.mean_ = self.mean
        
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
        self.model = self.isolation_forest
        
        # Calculate threshold based on scores
        scores = -self.isolation_forest.score_samples(data)
        if self.threshold is None:
            self.threshold = float(np.percentile(scores, 99))
    
    def _fit_one_class_svm(self, data) -> None:
        """Fit One-Class SVM"""
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
        
        try:
            from sklearn.svm import OneClassSVM
        except ImportError:
            logger.warning("OneClassSVM not available, falling back to Z-score method")
            self.method = 'zscore'
            self._fit_zscore(data)
            return
        
        # Ensure data is 2D numpy array
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        self.one_class_svm = OneClassSVM(
            kernel='rbf',
            gamma='auto',
            nu=0.1
        )
        self.one_class_svm.fit(data)
        self.model = self.one_class_svm
        
        # Calculate threshold based on decision function
        scores = -self.one_class_svm.decision_function(data)
        if self.threshold is None:
            self.threshold = float(np.percentile(scores, 90))
    
    def detect(self, data) -> list:
        """
        Detect anomalies in data
        
        Args:
            data: Data to check for anomalies (numpy array or list)
            
        Returns:
            Boolean mask (list or numpy array) indicating anomalies, or None if not fitted
        """
        if not self.fitted:
            logger.warning("Detector not fitted, returning None")
            return None
        
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
            Anomaly scores (higher = more anomalous), or None if not fitted
        """
        if not self.fitted:
            logger.warning("Detector not fitted, returning None")
            return None
        
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
        elif self.method == 'one_class_svm':
            return self._score_one_class_svm(data)
    
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
    
    def _score_one_class_svm(self, data) -> list:
        """Calculate One-Class SVM anomaly scores"""
        if self.one_class_svm is None:
            logger.warning("One-Class SVM not available, using Z-score fallback")
            return self._score_zscore(data)
        
        if not HAS_NUMPY:
            logger.warning("NumPy not available, using Z-score fallback")
            return self._score_zscore(data)
        
        # Ensure data is 2D numpy array
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        # Negative decision_function gives anomaly scores (higher = more anomalous)
        scores = -self.one_class_svm.decision_function(data)
        return scores.tolist()
    
    def get_anomaly_scores(self, data):
        """
        Get anomaly scores for data (alias for score method)
        
        Args:
            data: Data to score
            
        Returns:
            Anomaly scores or None if not fitted
        """
        if not self.fitted:
            return None
        
        try:
            return self.score(data)
        except Exception as e:
            logger.warning(f"Failed to get anomaly scores: {e}")
            return None
    
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
    
    def get_statistics(self) -> Optional[dict]:
        """
        Get detection statistics
        
        Returns:
            Dictionary with statistics or None if not fitted
        """
        if not self.fitted:
            return None
        
        stats = {
            'method': self.method,
            'threshold': self.threshold,
            'fitted': self.fitted
        }
        
        if self.mean is not None:
            stats['mean'] = self.mean
        if self.std is not None:
            stats['std'] = self.std
        if self.q1 is not None:
            stats['q1'] = self.q1
        if self.q3 is not None:
            stats['q3'] = self.q3
        if self.iqr is not None:
            stats['iqr'] = self.iqr
        
        return stats
    
    def evaluate(self, X, y_true) -> Optional[dict]:
        """
        Evaluate detector performance
        
        Args:
            X: Test data
            y_true: True anomaly labels (0=normal, 1=anomaly)
            
        Returns:
            Dictionary with evaluation metrics or None
        """
        if not self.fitted:
            return None
        
        try:
            # Get predictions
            predictions = self.detect(X)
            
            # Convert to arrays if needed
            if HAS_NUMPY:
                if not isinstance(y_true, np.ndarray):
                    y_true = np.array(y_true)
                if not isinstance(predictions, np.ndarray):
                    predictions = np.array(predictions)
            
            # Calculate metrics
            true_positives = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and predictions[i] == True)
            false_positives = sum(1 for i in range(len(y_true)) if y_true[i] == 0 and predictions[i] == True)
            true_negatives = sum(1 for i in range(len(y_true)) if y_true[i] == 0 and predictions[i] == False)
            false_negatives = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and predictions[i] == False)
            
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            accuracy = (true_positives + true_negatives) / len(y_true) if len(y_true) > 0 else 0.0
            
            return {
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'accuracy': accuracy,
                'true_positives': true_positives,
                'false_positives': false_positives,
                'true_negatives': true_negatives,
                'false_negatives': false_negatives
            }
        except Exception as e:
            logger.warning(f"Failed to evaluate: {e}")
            return None
    
    def save(self, filepath: str) -> bool:
        """
        Save detector to file
        
        Args:
            filepath: Path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pickle
            
            state = {
                'method': self.method,
                'threshold': self.threshold,
                'fitted': self.fitted,
                'is_fitted': self.is_fitted,
                'mean': self.mean,
                'mean_': self.mean_,
                'std': self.std,
                'q1': self.q1,
                'q3': self.q3,
                'iqr': self.iqr,
                'model': self.model,
                'isolation_forest': self.isolation_forest,
                'one_class_svm': self.one_class_svm
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(state, f)
            
            logger.info(f"Model saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load(self, filepath: str) -> bool:
        """
        Load detector from file
        
        Args:
            filepath: Path to load from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pickle
            
            with open(filepath, 'rb') as f:
                state = pickle.load(f)
            
            self.method = state.get('method', 'zscore')
            self.threshold = state.get('threshold')
            self.fitted = state.get('fitted', False)
            self.is_fitted = state.get('is_fitted', False)
            self.mean = state.get('mean')
            self.mean_ = state.get('mean_')
            self.std = state.get('std')
            self.q1 = state.get('q1')
            self.q3 = state.get('q3')
            self.iqr = state.get('iqr')
            self.model = state.get('model')
            self.isolation_forest = state.get('isolation_forest')
            self.one_class_svm = state.get('one_class_svm')
            
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
