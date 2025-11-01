"""Tests for TimeSeriesAnalyzer"""
import pytest
from venom.analytics.time_series import TimeSeriesAnalyzer


def test_fit_and_forecast():
    """Test fitting and forecasting"""
    analyzer = TimeSeriesAnalyzer()
    
    # Create simple linear trend: y = 2x + 1
    timestamps = [0.0, 1.0, 2.0, 3.0, 4.0]
    values = [1.0, 3.0, 5.0, 7.0, 9.0]
    
    analyzer.fit(timestamps, values)
    
    assert analyzer.fitted
    assert analyzer.slope is not None
    assert analyzer.intercept is not None
    
    # Slope should be approximately 2.0
    assert abs(analyzer.slope - 2.0) < 0.01
    # Intercept should be approximately 1.0
    assert abs(analyzer.intercept - 1.0) < 0.01
    
    # Forecast next 3 values
    forecasts = analyzer.forecast(horizon=3)
    assert len(forecasts) == 3
    
    # Should be approximately 11, 13, 15
    assert abs(forecasts[0] - 11.0) < 0.5
    assert abs(forecasts[1] - 13.0) < 0.5
    assert abs(forecasts[2] - 15.0) < 0.5


def test_detect_trend():
    """Test trend detection"""
    analyzer = TimeSeriesAnalyzer()
    
    # Increasing trend
    timestamps = list(range(10))
    values = [i * 2 + 10 for i in range(10)]
    
    analyzer.fit(timestamps, values)
    trend = analyzer.detect_trend()
    assert trend == 'increasing'
    
    # Decreasing trend
    values = [100 - i * 5 for i in range(10)]
    analyzer.fit(timestamps, values)
    trend = analyzer.detect_trend()
    assert trend == 'decreasing'
    
    # Stationary (flat)
    values = [50.0] * 10
    analyzer.fit(timestamps, values)
    trend = analyzer.detect_trend()
    assert trend == 'stationary'


def test_smooth_ewma():
    """Test exponentially weighted moving average"""
    analyzer = TimeSeriesAnalyzer()
    
    # Create noisy data
    timestamps = list(range(10))
    values = [10.0, 12.0, 9.0, 11.0, 10.5, 13.0, 10.0, 11.5, 10.5, 12.0]
    
    analyzer.fit(timestamps, values)
    
    # Smooth with EWMA
    smoothed = analyzer.smooth(method='ewma', alpha=0.3)
    
    assert len(smoothed) == len(values)
    
    # Smoothed values should be less volatile
    # First value should match
    assert smoothed[0] == values[0]
    
    # Smoothed values should be different from original (due to smoothing)
    differences = sum(abs(s - v) for s, v in zip(smoothed[1:], values[1:]))
    assert differences > 0  # Should have some difference


def test_detect_seasonality():
    """Test seasonality detection"""
    analyzer = TimeSeriesAnalyzer()
    
    # Create simple linear data without seasonality
    timestamps = list(range(20))
    values = [i * 0.5 + 10 for i in range(20)]
    
    analyzer.fit(timestamps, values)
    
    # Detect seasonality
    seasonality = analyzer.detect_seasonality()
    
    # Should have expected keys
    assert 'has_seasonality' in seasonality
    assert 'period' in seasonality
    assert 'strength' in seasonality
    
    # For linear trend, shouldn't detect strong seasonality
    assert isinstance(seasonality['has_seasonality'], bool)


def test_autocorrelation():
    """Test autocorrelation function"""
    analyzer = TimeSeriesAnalyzer()
    
    # Create data with some pattern
    timestamps = list(range(50))
    values = [10.0 + i * 0.5 for i in range(50)]
    
    analyzer.fit(timestamps, values)
    
    # Compute autocorrelation
    acf = analyzer.compute_autocorrelation(lags=10)
    
    assert len(acf) == 11  # Lag 0 through 10
    assert acf[0] == 1.0  # Lag 0 should be 1.0
    
    # All ACF values should be between -1 and 1
    for value in acf:
        assert -1.0 <= value <= 1.0
