"""
Stream Analytics for Real-Time Data Processing
Provides real-time data ingestion and anomaly detection
"""

import logging
from typing import List, Dict, Callable, Optional, Any
from collections import deque
import statistics

logger = logging.getLogger(__name__)

class StreamProcessor:
    """
    Real-time stream processor with anomaly detection
    Uses Z-score based anomaly detection with rolling window statistics
    """
    
    def __init__(self, window_size: int = 100, anomaly_threshold: float = 3.0):
        """
        Initialize stream processor
        
        Args:
            window_size: Size of the rolling window for statistics
            anomaly_threshold: Z-score threshold for anomaly detection (default 3.0)
        """
        self.window_size = window_size
        self.anomaly_threshold = anomaly_threshold
        self.data_window: deque = deque(maxlen=window_size)
        self.anomaly_handlers: List[Callable] = []
        self.total_processed = 0
        self.anomalies_detected = 0
        logger.info(f"StreamProcessor initialized with window_size={window_size}, threshold={anomaly_threshold}")
    
    def ingest(self, value: float) -> bool:
        """
        Ingest a single data point
        
        Args:
            value: Numeric data point to process
            
        Returns:
            True if anomaly detected, False otherwise
        """
        self.data_window.append(value)
        self.total_processed += 1
        
        # Check for anomaly if we have enough data
        if len(self.data_window) >= 3:  # Need at least 3 points for meaningful statistics
            is_anomaly = self._check_anomaly(value)
            if is_anomaly:
                self.anomalies_detected += 1
                self._trigger_handlers(value)
                logger.warning(f"Anomaly detected: value={value}")
                return True
        
        return False
    
    def _check_anomaly(self, value: float) -> bool:
        """
        Check if value is an anomaly using Z-score
        
        Args:
            value: Value to check
            
        Returns:
            True if anomaly, False otherwise
        """
        if len(self.data_window) < 3:
            return False
        
        try:
            mean = statistics.mean(self.data_window)
            stdev = statistics.stdev(self.data_window)
            
            # Avoid division by zero
            if stdev == 0:
                return False
            
            z_score = abs((value - mean) / stdev)
            return z_score > self.anomaly_threshold
        except Exception as e:
            logger.error(f"Error calculating Z-score: {e}")
            return False
    
    def register_handler(self, handler: Callable[[float], None]):
        """
        Register a callback handler for anomalies
        
        Args:
            handler: Callback function that takes anomaly value as argument
        """
        self.anomaly_handlers.append(handler)
        logger.info(f"Registered anomaly handler: {handler.__name__}")
    
    def _trigger_handlers(self, value: float):
        """
        Trigger all registered anomaly handlers
        
        Args:
            value: Anomaly value to pass to handlers
        """
        for handler in self.anomaly_handlers:
            try:
                handler(value)
            except Exception as e:
                logger.error(f"Error in anomaly handler {handler.__name__}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rolling window statistics
        
        Returns:
            Dict with mean, stdev, min, max, count, anomalies_detected
        """
        if len(self.data_window) == 0:
            return {
                "count": 0,
                "mean": 0.0,
                "stdev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "total_processed": self.total_processed,
                "anomalies_detected": self.anomalies_detected
            }
        
        try:
            data_list = list(self.data_window)
            mean = statistics.mean(data_list)
            stdev = statistics.stdev(data_list) if len(data_list) > 1 else 0.0
            
            return {
                "count": len(data_list),
                "mean": mean,
                "stdev": stdev,
                "min": min(data_list),
                "max": max(data_list),
                "total_processed": self.total_processed,
                "anomalies_detected": self.anomalies_detected
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {
                "error": str(e),
                "total_processed": self.total_processed,
                "anomalies_detected": self.anomalies_detected
            }
    
    def reset(self):
        """Reset the stream processor state"""
        self.data_window.clear()
        self.total_processed = 0
        self.anomalies_detected = 0
        logger.info("StreamProcessor reset")
