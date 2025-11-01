"""Tests for PredictiveEngine"""
import pytest
import os
import tempfile
from venom.analytics.predictor import PredictiveEngine

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def test_linear_regression():
    """Test linear regression model"""
    engine = PredictiveEngine(model_type='linear')
    
    # Create simple linear relationship: y = 2x + 3
    X = [[0], [1], [2], [3], [4], [5]]
    y = [3, 5, 7, 9, 11, 13]
    
    # Train the model
    metrics = engine.train(X, y)
    
    assert engine.trained
    assert 'mse' in metrics
    assert 'mae' in metrics
    
    # Predictions should be close to actual
    predictions = engine.predict(X)
    
    assert len(predictions) == len(y)
    
    # Check first and last predictions
    if HAS_NUMPY:
        assert abs(predictions[0] - 3.0) < 0.1
        assert abs(predictions[-1] - 13.0) < 0.1
    else:
        assert abs(predictions[0] - 3.0) < 0.5
        assert abs(predictions[-1] - 13.0) < 0.5


def test_random_forest():
    """Test random forest model"""
    try:
        import sklearn
        
        engine = PredictiveEngine(model_type='random_forest')
        
        # Create non-linear relationship
        X = [[i] for i in range(20)]
        y = [i ** 2 for i in range(20)]
        
        # Train the model
        metrics = engine.train(X, y, n_estimators=50)
        
        assert engine.trained
        assert 'mse' in metrics or 'mae' in metrics
        
        # Make predictions
        predictions = engine.predict([[5], [10], [15]])
        
        assert len(predictions) == 3
        
        # Predictions should be reasonable (quadratic relationship)
        assert predictions[0] > 0
        assert predictions[1] > predictions[0]
        assert predictions[2] > predictions[1]
        
    except ImportError:
        pytest.skip("scikit-learn not available")


def test_evaluate():
    """Test model evaluation"""
    engine = PredictiveEngine(model_type='linear')
    
    # Training data
    X_train = [[i] for i in range(10)]
    y_train = [2 * i + 1 for i in range(10)]
    
    # Test data
    X_test = [[i] for i in range(10, 15)]
    y_test = [2 * i + 1 for i in range(10, 15)]
    
    # Train
    engine.train(X_train, y_train)
    
    # Evaluate
    metrics = engine.evaluate(X_test, y_test)
    
    assert 'mae' in metrics
    assert 'mse' in metrics
    assert 'rmse' in metrics
    
    # For perfect linear relationship, error should be very small
    assert metrics['mae'] < 1.0
    assert metrics['mse'] < 2.0


def test_feature_importance():
    """Test feature importance extraction"""
    engine = PredictiveEngine(model_type='linear')
    
    if not HAS_NUMPY:
        pytest.skip("NumPy not available")
    
    import numpy as np
    
    # Create data with multiple features
    X = np.random.rand(50, 3)
    # y depends more on first feature
    y = 5 * X[:, 0] + 1 * X[:, 1] + 0.5 * X[:, 2] + 2
    
    # Train
    engine.train(X, y)
    
    # Get feature importance
    importance = engine.feature_importance()
    
    assert len(importance) == 3
    assert 'feature_0' in importance
    assert 'feature_1' in importance
    assert 'feature_2' in importance
    
    # All importance values should be non-negative
    for value in importance.values():
        assert value >= 0


def test_model_persistence():
    """Test saving and loading models"""
    engine = PredictiveEngine(model_type='linear')
    
    # Training data
    X = [[i] for i in range(10)]
    y = [2 * i + 1 for i in range(10)]
    
    # Train
    engine.train(X, y)
    
    # Make predictions before saving
    predictions_before = engine.predict([[5], [10]])
    
    # Save model to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_path = f.name
    
    try:
        engine.save_model(temp_path)
        
        # Create new engine and load
        new_engine = PredictiveEngine()
        new_engine.load_model(temp_path)
        
        assert new_engine.trained
        assert new_engine.model_type == 'linear'
        
        # Make predictions after loading
        predictions_after = new_engine.predict([[5], [10]])
        
        # Predictions should be the same
        assert len(predictions_before) == len(predictions_after)
        
        if HAS_NUMPY:
            import numpy as np
            assert np.allclose(predictions_before, predictions_after)
        else:
            for before, after in zip(predictions_before, predictions_after):
                assert abs(before - after) < 0.01
    
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
