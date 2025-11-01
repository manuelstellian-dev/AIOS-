"""
VENOM Time Series Analyzer - Time series analysis and forecasting
Provides trend detection, seasonality analysis, and forecasting capabilities
"""

import logging
from typing import List, Dict, Any, Optional
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
    from scipy import fft
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("SciPy not available, FFT-based seasonality detection disabled")


class TimeSeriesAnalyzer:
    """
    Time series analysis with trend detection, seasonality, and forecasting
    """
    
    def __init__(self):
        """Initialize time series analyzer"""
        self.timestamps: List[float] = []
        self.values: List[float] = []
        self.fitted = False
        self.slope: Optional[float] = None
        self.intercept: Optional[float] = None
        logger.info("TimeSeriesAnalyzer initialized")
    
    def fit(self, timestamps: List[float], values: List[float]) -> None:
        """
        Fit the analyzer on time series data
        
        Args:
            timestamps: List of timestamps
            values: List of corresponding values
        """
        if len(timestamps) != len(values):
            raise ValueError("timestamps and values must have same length")
        
        if len(timestamps) < 2:
            raise ValueError("Need at least 2 data points")
        
        self.timestamps = timestamps.copy()
        self.values = values.copy()
        
        # Fit linear regression for trend
        self._fit_linear_regression()
        self.fitted = True
        logger.info(f"Fitted on {len(timestamps)} data points")
    
    def _fit_linear_regression(self) -> None:
        """Fit simple linear regression"""
        n = len(self.timestamps)
        
        if HAS_NUMPY:
            # Use numpy for better numerical stability
            X = np.array(self.timestamps)
            y = np.array(self.values)
            
            # Calculate slope and intercept
            x_mean = np.mean(X)
            y_mean = np.mean(y)
            
            numerator = np.sum((X - x_mean) * (y - y_mean))
            denominator = np.sum((X - x_mean) ** 2)
            
            if denominator != 0:
                self.slope = numerator / denominator
                self.intercept = y_mean - self.slope * x_mean
            else:
                self.slope = 0.0
                self.intercept = y_mean
        else:
            # Fallback to pure Python
            x_mean = statistics.mean(self.timestamps)
            y_mean = statistics.mean(self.values)
            
            numerator = sum((x - x_mean) * (y - y_mean) 
                          for x, y in zip(self.timestamps, self.values))
            denominator = sum((x - x_mean) ** 2 for x in self.timestamps)
            
            if denominator != 0:
                self.slope = numerator / denominator
                self.intercept = y_mean - self.slope * x_mean
            else:
                self.slope = 0.0
                self.intercept = y_mean
    
    def forecast(self, horizon: int = 10) -> List[float]:
        """
        Forecast future values
        
        Args:
            horizon: Number of steps to forecast
            
        Returns:
            List of forecasted values
        """
        if not self.fitted:
            raise RuntimeError("Must call fit() before forecast()")
        
        # Use simple exponential smoothing
        last_timestamp = self.timestamps[-1]
        timestamp_step = self.timestamps[-1] - self.timestamps[-2] if len(self.timestamps) > 1 else 1.0
        
        forecasts = []
        for i in range(1, horizon + 1):
            future_timestamp = last_timestamp + i * timestamp_step
            # Linear extrapolation
            forecast_value = self.slope * future_timestamp + self.intercept
            forecasts.append(forecast_value)
        
        return forecasts
    
    def detect_trend(self) -> str:
        """
        Detect trend direction
        
        Returns:
            'increasing', 'decreasing', or 'stationary'
        """
        if not self.fitted:
            raise RuntimeError("Must call fit() before detect_trend()")
        
        # Use slope to determine trend
        threshold = 0.01 * abs(statistics.mean(self.values))
        
        if abs(self.slope) < threshold:
            return 'stationary'
        elif self.slope > 0:
            return 'increasing'
        else:
            return 'decreasing'
    
    def detect_seasonality(self) -> Dict[str, Any]:
        """
        Detect seasonality in the time series
        
        Returns:
            Dictionary with seasonality information
        """
        if not self.fitted:
            raise RuntimeError("Must call fit() before detect_seasonality()")
        
        result = {
            'has_seasonality': False,
            'period': None,
            'strength': 0.0
        }
        
        if not HAS_SCIPY or len(self.values) < 10:
            logger.warning("SciPy not available or insufficient data for seasonality detection")
            return result
        
        try:
            # Detrend the data
            detrended = []
            for i, (t, v) in enumerate(zip(self.timestamps, self.values)):
                trend_value = self.slope * t + self.intercept
                detrended.append(v - trend_value)
            
            # Apply FFT
            fft_values = fft.fft(detrended)
            power = np.abs(fft_values) ** 2
            
            # Find dominant frequency (excluding DC component)
            n = len(power)
            half_n = n // 2
            
            if half_n > 1:
                # Look at first half of spectrum (positive frequencies)
                dominant_idx = np.argmax(power[1:half_n]) + 1
                
                if power[dominant_idx] > np.mean(power[1:half_n]) * 2:
                    result['has_seasonality'] = True
                    result['period'] = n / dominant_idx
                    result['strength'] = float(power[dominant_idx] / np.sum(power[1:half_n]))
        
        except Exception as e:
            logger.error(f"Error detecting seasonality: {e}")
        
        return result
    
    def smooth(self, method: str = 'ewma', alpha: float = 0.3) -> List[float]:
        """
        Smooth the time series
        
        Args:
            method: Smoothing method ('ewma' for exponentially weighted moving average)
            alpha: Smoothing parameter (0 < alpha <= 1)
            
        Returns:
            Smoothed values
        """
        if not self.fitted:
            raise RuntimeError("Must call fit() before smooth()")
        
        if not (0 < alpha <= 1):
            raise ValueError("alpha must be in range (0, 1]")
        
        if method == 'ewma':
            smoothed = [self.values[0]]  # Start with first value
            
            for value in self.values[1:]:
                new_value = alpha * value + (1 - alpha) * smoothed[-1]
                smoothed.append(new_value)
            
            return smoothed
        else:
            raise ValueError(f"Unknown smoothing method: {method}")
    
    def compute_autocorrelation(self, lags: int = 20) -> List[float]:
        """
        Compute autocorrelation function
        
        Args:
            lags: Number of lags to compute
            
        Returns:
            List of autocorrelation values
        """
        if not self.fitted:
            raise RuntimeError("Must call fit() before compute_autocorrelation()")
        
        n = len(self.values)
        if lags >= n:
            lags = n - 1
        
        # Calculate mean
        mean = statistics.mean(self.values)
        
        # Calculate variance
        variance = sum((v - mean) ** 2 for v in self.values) / n
        
        if variance == 0:
            return [1.0] + [0.0] * lags
        
        # Calculate autocorrelations
        acf = [1.0]  # Lag 0 is always 1
        
        for lag in range(1, lags + 1):
            covariance = sum((self.values[i] - mean) * (self.values[i - lag] - mean)
                           for i in range(lag, n)) / n
            acf.append(covariance / variance)
        
        return acf
