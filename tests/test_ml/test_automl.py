"""Tests for AutoML Pipeline"""
import pytest
import pandas as pd
import numpy as np
from venom.ml.automl import AutoMLPipeline


@pytest.fixture
def pipeline():
    """Create AutoML pipeline for testing"""
    return AutoMLPipeline(framework='optuna')


def test_tune_hyperparameters(pipeline):
    """Test hyperparameter tuning"""
    if not pipeline.is_available():
        pytest.skip("optuna not available")
        
    # Define simple objective function
    def objective(params):
        # Simulate model training - return metric based on params
        x = params.get('x', 0.5)
        y = params.get('y', 0.5)
        return -(x - 0.7)**2 - (y - 0.3)**2  # Maximize this (peak at x=0.7, y=0.3)
        
    # Define search space
    search_space = {
        'x': {'type': 'float', 'low': 0.0, 'high': 1.0},
        'y': {'type': 'float', 'low': 0.0, 'high': 1.0}
    }
    
    result = pipeline.tune_hyperparameters(
        objective_fn=objective,
        search_space=search_space,
        n_trials=10,
        direction='maximize'
    )
    
    assert 'best_params' in result
    assert 'best_value' in result
    assert 'best_trial' in result
    assert 'x' in result['best_params']
    assert 'y' in result['best_params']
    assert result['n_trials'] == 10


def test_optuna_integration(pipeline):
    """Test Optuna integration with different parameter types"""
    if not pipeline.is_available():
        pytest.skip("optuna not available")
        
    def objective(params):
        learning_rate = params.get('learning_rate', 0.01)
        n_layers = params.get('n_layers', 2)
        activation = params.get('activation', 'relu')
        
        # Simple mock metric
        score = learning_rate * n_layers
        if activation == 'relu':
            score *= 1.2
        return score
        
    search_space = {
        'learning_rate': {'type': 'float', 'low': 0.001, 'high': 0.1, 'log': True},
        'n_layers': {'type': 'int', 'low': 1, 'high': 5},
        'activation': {'type': 'categorical', 'choices': ['relu', 'tanh', 'sigmoid']}
    }
    
    result = pipeline.tune_hyperparameters(
        objective_fn=objective,
        search_space=search_space,
        n_trials=5,
        direction='maximize'
    )
    
    assert 'learning_rate' in result['best_params']
    assert 'n_layers' in result['best_params']
    assert 'activation' in result['best_params']


def test_search_space(pipeline):
    """Test different search space configurations"""
    if not pipeline.is_available():
        pytest.skip("optuna not available")
        
    def objective(params):
        return sum(params.values()) if isinstance(list(params.values())[0], (int, float)) else 0
        
    # Test integer search space
    search_space = {
        'param1': {'type': 'int', 'low': 0, 'high': 10},
        'param2': {'type': 'int', 'low': 5, 'high': 15}
    }
    
    result = pipeline.tune_hyperparameters(
        objective_fn=objective,
        search_space=search_space,
        n_trials=5,
        direction='maximize'
    )
    
    assert isinstance(result['best_params']['param1'], int)
    assert isinstance(result['best_params']['param2'], int)


def test_direction(pipeline):
    """Test minimize and maximize directions"""
    if not pipeline.is_available():
        pytest.skip("optuna not available")
        
    def objective(params):
        x = params.get('x', 0.5)
        return x  # Linear function
        
    search_space = {
        'x': {'type': 'float', 'low': 0.0, 'high': 1.0}
    }
    
    # Maximize - should find x close to 1.0
    result_max = pipeline.tune_hyperparameters(
        objective_fn=objective,
        search_space=search_space,
        n_trials=10,
        direction='maximize'
    )
    assert result_max['best_params']['x'] > 0.5
    
    # Minimize - should find x close to 0.0
    result_min = pipeline.tune_hyperparameters(
        objective_fn=objective,
        search_space=search_space,
        n_trials=10,
        direction='minimize'
    )
    assert result_min['best_params']['x'] < 0.5
    
    # Test invalid direction
    with pytest.raises(ValueError):
        pipeline.tune_hyperparameters(
            objective_fn=objective,
            search_space=search_space,
            n_trials=5,
            direction='invalid'
        )


def test_graceful_fallback():
    """Test graceful fallback when optuna not installed"""
    pipeline = AutoMLPipeline()
    
    if pipeline.is_available():
        pytest.skip("optuna is available, cannot test fallback")
        
    # Should not raise during initialization
    assert not pipeline.is_available()
    
    # Should raise when trying to use
    with pytest.raises(RuntimeError):
        pipeline.tune_hyperparameters(
            objective_fn=lambda x: 0,
            search_space={'x': {'type': 'float', 'low': 0, 'high': 1}},
            n_trials=5
        )


def test_auto_feature_engineering():
    """Test automatic feature engineering"""
    # Create test DataFrame
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [2, 4, 6, 8, 10],
        'feature3': [0.5, 1.0, 1.5, 2.0, 2.5],
        'category': ['A', 'B', 'A', 'B', 'A']
    })
    
    pipeline = AutoMLPipeline()
    df_engineered = pipeline.auto_feature_engineering(df)
    
    # Check that new features were created
    assert len(df_engineered.columns) > len(df.columns)
    
    # Check for squared features
    assert 'feature1_squared' in df_engineered.columns
    assert 'feature2_squared' in df_engineered.columns
    
    # Check for interaction features
    assert 'feature1_feature2_interaction' in df_engineered.columns
    
    # Check values are correct
    assert df_engineered['feature1_squared'].iloc[0] == 1
    assert df_engineered['feature1_squared'].iloc[1] == 4
