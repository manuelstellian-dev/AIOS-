"""
Predictive Analytics for Threat Forecasting
Uses simple linear regression for time series prediction and trend analysis
"""

import logging
from typing import List, Dict, Tuple, Optional, Any
import statistics

logger = logging.getLogger(__name__)

class PredictiveModel:
    """
    Predictive Model for threat forecasting and trend analysis
    Uses simple linear regression on historical data
    """
    
    def __init__(self):
        self.history: List[Tuple[float, float]] = []  # (timestamp, value) pairs
        self.slope: Optional[float] = None
        self.intercept: Optional[float] = None
        self.trained: bool = False
        logger.info("PredictiveModel initialized")
    
    def train_on_history(self, history: List[Tuple[float, float]]) -> bool:
        """
        Train the model on historical data using simple linear regression
        
        Args:
            history: List of (timestamp, value) tuples
            
        Returns:
            True if training successful, False otherwise
        """
        if len(history) < 2:
            logger.error("Need at least 2 data points for training")
            return False
        
        self.history = history.copy()
        
        try:
            # Extract x (timestamps) and y (values)
            x_values = [point[0] for point in history]
            y_values = [point[1] for point in history]
            
            # Calculate means
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(y_values)
            
            # Calculate slope and intercept using least squares
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            if denominator == 0:
                logger.error("Cannot train: all timestamps are identical")
                return False
            
            self.slope = numerator / denominator
            self.intercept = y_mean - self.slope * x_mean
            self.trained = True
            
            logger.info(f"Model trained: slope={self.slope:.4f}, intercept={self.intercept:.4f}")
            return True
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False
    
    def forecast_threat(self, timestamp: float) -> Optional[float]:
        """
        Forecast threat level at a future timestamp
        
        Args:
            timestamp: Future timestamp to predict
            
        Returns:
            Predicted threat level, or None if model not trained
        """
        if not self.trained:
            logger.error("Model not trained - call train_on_history first")
            return None
        
        try:
            prediction = self.slope * timestamp + self.intercept
            logger.debug(f"Forecast for t={timestamp}: {prediction:.4f}")
            return prediction
        except Exception as e:
            logger.error(f"Forecast failed: {e}")
            return None
    
    def confidence_intervals(self, timestamp: float, confidence_level: float = 0.95) -> Optional[Dict[str, float]]:
        """
        Calculate confidence intervals for a prediction
        Uses standard error of estimate
        
        Args:
            timestamp: Timestamp to predict
            confidence_level: Confidence level (default 0.95 for 95%)
            
        Returns:
            Dict with prediction, lower_bound, upper_bound, or None if not trained
        """
        if not self.trained:
            logger.error("Model not trained - call train_on_history first")
            return None
        
        try:
            prediction = self.forecast_threat(timestamp)
            if prediction is None:
                return None
            
            # Calculate standard error of estimate
            x_values = [point[0] for point in self.history]
            y_values = [point[1] for point in self.history]
            
            # Calculate residuals
            predictions = [self.slope * x + self.intercept for x in x_values]
            residuals = [(y - pred) ** 2 for y, pred in zip(y_values, predictions)]
            
            n = len(self.history)
            if n <= 2:
                # Not enough data for meaningful confidence intervals
                margin = 0.5
            else:
                # Standard error of estimate
                standard_error = (sum(residuals) / (n - 2)) ** 0.5
                
                # Calculate distance from mean of x values
                x_mean = statistics.mean(x_values)
                x_variance = sum((x - x_mean) ** 2 for x in x_values)
                
                # Prediction interval
                # Using simplified t-value of 2 for 95% confidence
                t_value = 2.0 if confidence_level >= 0.95 else 1.5
                
                margin = t_value * standard_error * (1 + 1/n + (timestamp - x_mean)**2 / x_variance) ** 0.5
                
                # Ensure minimum margin for perfect fits
                if margin < 0.1:
                    margin = 0.1
            
            return {
                "prediction": prediction,
                "lower_bound": prediction - margin,
                "upper_bound": prediction + margin,
                "confidence_level": confidence_level
            }
        except Exception as e:
            logger.error(f"Confidence interval calculation failed: {e}")
            return None
    
    def get_trend(self) -> Optional[str]:
        """
        Get trend direction based on slope
        
        Returns:
            "increasing", "decreasing", or "stable", or None if not trained
        """
        if not self.trained:
            logger.error("Model not trained - call train_on_history first")
            return None
        
        try:
            # Define threshold for "stable" trend
            threshold = 0.01
            
            if abs(self.slope) < threshold:
                trend = "stable"
            elif self.slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            logger.debug(f"Trend: {trend} (slope={self.slope:.4f})")
            return trend
        except Exception as e:
            logger.error(f"Trend calculation failed: {e}")
            return None
    
    def get_model_stats(self) -> Dict[str, Any]:
        """
        Get model statistics and performance metrics
        
        Returns:
            Dict with training status, parameters, and metrics
        """
        if not self.trained:
            return {
                "trained": False,
                "data_points": len(self.history)
            }
        
        try:
            # Calculate R-squared
            y_values = [point[1] for point in self.history]
            y_mean = statistics.mean(y_values)
            
            # Total sum of squares
            ss_total = sum((y - y_mean) ** 2 for y in y_values)
            
            # Residual sum of squares
            predictions = [self.slope * x + self.intercept for x, _ in self.history]
            ss_residual = sum((y - pred) ** 2 for y, pred in zip(y_values, predictions))
            
            # R-squared
            r_squared = 1 - (ss_residual / ss_total) if ss_total > 0 else 0.0
            
            return {
                "trained": True,
                "data_points": len(self.history),
                "slope": self.slope,
                "intercept": self.intercept,
                "r_squared": r_squared,
                "trend": self.get_trend()
            }
        except Exception as e:
            logger.error(f"Stats calculation failed: {e}")
            return {
                "trained": True,
                "data_points": len(self.history),
                "slope": self.slope,
                "intercept": self.intercept,
                "error": str(e)
            }
