"""Test Predictive Analytics"""
import pytest
from venom.analytics.predictive import PredictiveModel

def test_predictive_model_init():
    """Test predictive model initializes"""
    model = PredictiveModel()
    assert model is not None
    assert model.trained == False

def test_predictive_model_train():
    """Test training on historical data"""
    model = PredictiveModel()
    
    # Simple upward trend: y = 2x + 1
    history = [
        (0.0, 1.0),
        (1.0, 3.0),
        (2.0, 5.0),
        (3.0, 7.0),
        (4.0, 9.0)
    ]
    
    success = model.train_on_history(history)
    assert success == True
    assert model.trained == True
    assert model.slope is not None
    assert model.intercept is not None
    
    # Slope should be approximately 2.0
    assert abs(model.slope - 2.0) < 0.01
    # Intercept should be approximately 1.0
    assert abs(model.intercept - 1.0) < 0.01

def test_predictive_model_forecast():
    """Test threat forecasting"""
    model = PredictiveModel()
    
    # Linear trend: y = 2x + 1
    history = [
        (0.0, 1.0),
        (1.0, 3.0),
        (2.0, 5.0),
        (3.0, 7.0)
    ]
    
    model.train_on_history(history)
    
    # Forecast at t=5: should be approximately 11.0 (2*5 + 1)
    forecast = model.forecast_threat(5.0)
    assert forecast is not None
    assert abs(forecast - 11.0) < 0.1
    
    # Forecast at t=10: should be approximately 21.0 (2*10 + 1)
    forecast = model.forecast_threat(10.0)
    assert forecast is not None
    assert abs(forecast - 21.0) < 0.1

def test_predictive_model_confidence_intervals():
    """Test confidence interval calculation"""
    model = PredictiveModel()
    
    # Linear trend with small variation
    history = [
        (0.0, 1.0),
        (1.0, 3.0),
        (2.0, 5.0),
        (3.0, 7.0),
        (4.0, 9.0)
    ]
    
    model.train_on_history(history)
    
    intervals = model.confidence_intervals(5.0)
    assert intervals is not None
    assert "prediction" in intervals
    assert "lower_bound" in intervals
    assert "upper_bound" in intervals
    assert "confidence_level" in intervals
    
    # Prediction should be approximately 11.0
    assert abs(intervals["prediction"] - 11.0) < 0.1
    
    # Lower bound should be less than prediction
    assert intervals["lower_bound"] < intervals["prediction"]
    
    # Upper bound should be greater than prediction
    assert intervals["upper_bound"] > intervals["prediction"]

def test_predictive_model_get_trend():
    """Test trend detection"""
    model = PredictiveModel()
    
    # Test increasing trend
    history_increasing = [
        (0.0, 1.0),
        (1.0, 3.0),
        (2.0, 5.0)
    ]
    model.train_on_history(history_increasing)
    assert model.get_trend() == "increasing"
    
    # Test decreasing trend
    history_decreasing = [
        (0.0, 10.0),
        (1.0, 8.0),
        (2.0, 6.0)
    ]
    model.train_on_history(history_decreasing)
    assert model.get_trend() == "decreasing"
    
    # Test stable trend
    history_stable = [
        (0.0, 5.0),
        (1.0, 5.001),
        (2.0, 4.999)
    ]
    model.train_on_history(history_stable)
    assert model.get_trend() == "stable"
