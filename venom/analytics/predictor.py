"""
VENOM Predictive Engine - Predictive modeling and ML inference
Provides linear regression, random forest, and XGBoost models with graceful fallbacks
"""

import logging
import pickle
from typing import Dict, Optional, Any
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
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("scikit-learn not available, Random Forest disabled")

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.warning("XGBoost not available, XGBoost models disabled")


class PredictiveEngine:
    """
    Predictive modeling engine with multiple algorithms
    Supports linear regression, random forest, and XGBoost
    """
    
    def __init__(self, model_type: str = 'linear'):
        """
        Initialize predictive engine
        
        Args:
            model_type: Type of model ('linear', 'random_forest', 'xgboost')
        """
        valid_types = ['linear', 'random_forest', 'xgboost']
        if model_type not in valid_types:
            raise ValueError(f"model_type must be one of {valid_types}, got '{model_type}'")
        
        self.model_type = model_type
        self.model = None
        self.trained = False
        self.feature_names = None
        self.is_classifier = False
        
        # Linear regression parameters
        self.weights = None
        self.bias = None
        
        logger.info(f"PredictiveEngine initialized with model_type='{model_type}'")
    
    def train(self, X, y, **kwargs) -> Dict:
        """
        Train the model
        
        Args:
            X: Training features (numpy array or list)
            y: Training targets (numpy array or list)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary with training metrics
        """
        # Convert to numpy if available
        if HAS_NUMPY:
            if not isinstance(X, np.ndarray):
                X = np.array(X)
            if not isinstance(y, np.ndarray):
                y = np.array(y)
            
            if X.ndim == 1:
                X = X.reshape(-1, 1)
        else:
            # Ensure X is list of lists
            if isinstance(X, list) and len(X) > 0 and not isinstance(X[0], list):
                X = [[x] for x in X]
            if not isinstance(y, list):
                y = list(y)
        
        # Detect if this is classification (discrete target values)
        if HAS_NUMPY:
            unique_values = len(np.unique(y))
            self.is_classifier = unique_values < 20 and unique_values < len(y) / 2
        else:
            unique_values = len(set(y))
            self.is_classifier = unique_values < 20 and unique_values < len(y) / 2
        
        if self.model_type == 'linear':
            metrics = self._train_linear(X, y)
        elif self.model_type == 'random_forest':
            metrics = self._train_random_forest(X, y, **kwargs)
        elif self.model_type == 'xgboost':
            metrics = self._train_xgboost(X, y, **kwargs)
        
        self.trained = True
        logger.info(f"Training completed: {metrics}")
        return metrics
    
    def _train_linear(self, X, y) -> Dict:
        """Train linear regression model"""
        if HAS_NUMPY:
            # Add bias term
            X_with_bias = np.column_stack([np.ones(len(X)), X])
            
            # Solve normal equations: (X^T X)^-1 X^T y
            try:
                XtX = X_with_bias.T @ X_with_bias
                Xty = X_with_bias.T @ y
                params = np.linalg.solve(XtX, Xty)
                
                self.bias = params[0]
                self.weights = params[1:]
            except np.linalg.LinAlgError:
                logger.warning("Singular matrix, using pseudo-inverse")
                params = np.linalg.lstsq(X_with_bias, y, rcond=None)[0]
                self.bias = params[0]
                self.weights = params[1:]
            
            # Calculate metrics (compute predictions directly)
            y_pred = X @ self.weights + self.bias
            mse = float(np.mean((y - y_pred) ** 2))
            mae = float(np.mean(np.abs(y - y_pred)))
            
            # R-squared
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            ss_res = np.sum((y - y_pred) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
            
            # Set model attribute for consistency
            self.model = {
                'type': 'linear',
                'weights': self.weights,
                'bias': self.bias
            }
            
            return {
                'mse': mse,
                'rmse': mse ** 0.5,
                'mae': mae,
                'r2': float(r2)
            }
        else:
            # Fallback: simple linear regression for 1D case
            if len(X[0]) == 1:
                x_values = [row[0] for row in X]
                x_mean = statistics.mean(x_values)
                y_mean = statistics.mean(y)
                
                numerator = sum((x - x_mean) * (y_val - y_mean) 
                              for x, y_val in zip(x_values, y))
                denominator = sum((x - x_mean) ** 2 for x in x_values)
                
                if denominator != 0:
                    self.weights = [numerator / denominator]
                    self.bias = y_mean - self.weights[0] * x_mean
                else:
                    self.weights = [0.0]
                    self.bias = y_mean
                
                # Calculate metrics
                y_pred = [self.weights[0] * x + self.bias for x in x_values]
                errors = [abs(y_val - pred) for y_val, pred in zip(y, y_pred)]
                squared_errors = [e ** 2 for e in errors]
                
                mse = statistics.mean(squared_errors)
                mae = statistics.mean(errors)
                
                # Set model attribute for consistency
                self.model = {
                    'type': 'linear',
                    'weights': self.weights,
                    'bias': self.bias
                }
                
                return {
                    'mse': mse,
                    'rmse': mse ** 0.5,
                    'mae': mae,
                    'r2': 0.0  # Simplified
                }
            else:
                raise NotImplementedError("Multi-feature linear regression requires NumPy")
    
    def _train_random_forest(self, X, y, **kwargs) -> Dict:
        """Train random forest model"""
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not available, falling back to linear model")
            self.model_type = 'linear'
            return self._train_linear(X, y)
        
        if not HAS_NUMPY:
            logger.warning("NumPy not available, falling back to linear model")
            self.model_type = 'linear'
            return self._train_linear(X, y)
        
        # Choose regressor or classifier
        if self.is_classifier:
            self.model = RandomForestClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', None),
                random_state=42
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', None),
                random_state=42
            )
        
        self.model.fit(X, y)
        
        # Calculate metrics
        y_pred = self.model.predict(X)
        
        if self.is_classifier:
            accuracy = accuracy_score(y, y_pred)
            return {'accuracy': float(accuracy)}
        else:
            mse = mean_squared_error(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                'mse': float(mse),
                'rmse': float(mse ** 0.5),
                'mae': float(mae),
                'r2': float(r2)
            }
    
    def _train_xgboost(self, X, y, **kwargs) -> Dict:
        """Train XGBoost model"""
        if not HAS_XGBOOST:
            logger.warning("XGBoost not available, falling back to random forest")
            self.model_type = 'random_forest'
            return self._train_random_forest(X, y, **kwargs)
        
        if not HAS_NUMPY:
            logger.warning("NumPy not available, falling back to linear model")
            self.model_type = 'linear'
            return self._train_linear(X, y)
        
        # Choose regressor or classifier
        if self.is_classifier:
            self.model = xgb.XGBClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 6),
                learning_rate=kwargs.get('learning_rate', 0.1),
                random_state=42
            )
        else:
            self.model = xgb.XGBRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 6),
                learning_rate=kwargs.get('learning_rate', 0.1),
                random_state=42
            )
        
        self.model.fit(X, y)
        
        # Calculate metrics
        y_pred = self.model.predict(X)
        
        if self.is_classifier:
            if HAS_SKLEARN:
                accuracy = accuracy_score(y, y_pred)
                return {'accuracy': float(accuracy)}
            else:
                # Fallback accuracy calculation
                correct = sum(1 for true, pred in zip(y, y_pred) if abs(true - pred) < 0.5)
                accuracy = correct / len(y)
                return {'accuracy': float(accuracy)}
        else:
            if HAS_SKLEARN:
                mse = mean_squared_error(y, y_pred)
                mae = mean_absolute_error(y, y_pred)
                r2 = r2_score(y, y_pred)
            else:
                # Fallback metrics
                errors = [abs(true - pred) for true, pred in zip(y, y_pred)]
                squared_errors = [e ** 2 for e in errors]
                mse = statistics.mean(squared_errors)
                mae = statistics.mean(errors)
                r2 = 0.0
            
            return {
                'mse': float(mse),
                'rmse': float(mse ** 0.5),
                'mae': float(mae),
                'r2': float(r2)
            }
    
    def predict(self, X):
        """
        Make predictions
        
        Args:
            X: Features to predict (numpy array or list)
            
        Returns:
            Predictions (numpy array or list), or None if not trained
        """
        if not self.trained:
            logger.warning("Model not trained, returning None")
            return None
        
        if HAS_NUMPY:
            if not isinstance(X, np.ndarray):
                X = np.array(X)
            
            if X.ndim == 1:
                X = X.reshape(-1, 1)
        else:
            # Ensure X is list of lists
            if isinstance(X, list) and len(X) > 0 and not isinstance(X[0], list):
                X = [[x] for x in X]
        
        if self.model_type == 'linear':
            if HAS_NUMPY:
                predictions = X @ self.weights + self.bias
                return predictions
            else:
                # Fallback for 1D case
                predictions = [sum(w * x for w, x in zip(self.weights, row)) + self.bias 
                             for row in X]
                return predictions
        else:
            # Random forest or XGBoost
            if self.model is None:
                raise RuntimeError("Model not trained")
            return self.model.predict(X)
    
    def evaluate(self, X, y) -> Dict[str, float]:
        """
        Evaluate model on test data
        
        Args:
            X: Test features
            y: Test targets
            
        Returns:
            Dictionary with evaluation metrics
        """
        if not self.trained:
            raise RuntimeError("Must call train() before evaluate()")
        
        y_pred = self.predict(X)
        
        if HAS_NUMPY:
            if not isinstance(y, np.ndarray):
                y = np.array(y)
            if not isinstance(y_pred, np.ndarray):
                y_pred = np.array(y_pred)
        
        if self.is_classifier:
            if HAS_SKLEARN:
                accuracy = accuracy_score(y, y_pred)
                return {'accuracy': float(accuracy)}
            else:
                # Fallback accuracy calculation
                correct = sum(1 for true, pred in zip(y, y_pred) if abs(true - pred) < 0.5)
                accuracy = correct / len(y)
                return {'accuracy': float(accuracy)}
        else:
            if HAS_SKLEARN and HAS_NUMPY:
                mse = mean_squared_error(y, y_pred)
                mae = mean_absolute_error(y, y_pred)
                r2 = r2_score(y, y_pred)
            else:
                # Fallback metrics
                errors = [abs(true - pred) for true, pred in zip(y, y_pred)]
                squared_errors = [e ** 2 for e in errors]
                mse = statistics.mean(squared_errors)
                mae = statistics.mean(errors)
                r2 = 0.0
            
            return {
                'mae': float(mae),
                'mse': float(mse),
                'rmse': float(mse ** 0.5),
                'r2': float(r2)
            }
    
    def feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores
        
        Returns:
            Dictionary mapping feature names/indices to importance scores
        """
        if not self.trained:
            raise RuntimeError("Must call train() before feature_importance()")
        
        if self.model_type == 'linear':
            # For linear models, use absolute weights as importance
            if self.weights is None:
                return {}
            
            importance = {}
            if HAS_NUMPY:
                weights_abs = np.abs(self.weights)
                total = np.sum(weights_abs)
                if total > 0:
                    normalized = weights_abs / total
                else:
                    normalized = weights_abs
                
                for i, imp in enumerate(normalized):
                    feature_name = f'feature_{i}' if self.feature_names is None else self.feature_names[i]
                    importance[feature_name] = float(imp)
            else:
                weights_abs = [abs(w) for w in self.weights]
                total = sum(weights_abs)
                
                for i, w_abs in enumerate(weights_abs):
                    feature_name = f'feature_{i}' if self.feature_names is None else self.feature_names[i]
                    importance[feature_name] = w_abs / total if total > 0 else 0.0
            
            return importance
        
        elif self.model_type in ['random_forest', 'xgboost']:
            if self.model is None:
                return {}
            
            # Get feature importances from the model
            importances = self.model.feature_importances_
            
            importance = {}
            for i, imp in enumerate(importances):
                feature_name = f'feature_{i}' if self.feature_names is None else self.feature_names[i]
                importance[feature_name] = float(imp)
            
            return importance
        
        return {}
    
    def save_model(self, path: str) -> bool:
        """
        Save model to file
        
        Args:
            path: Path to save the model
            
        Returns:
            True if successful, False otherwise
        """
        if not self.trained:
            logger.warning("Model not trained, cannot save")
            return False
        
        try:
            model_data = {
                'model_type': self.model_type,
                'trained': self.trained,
                'is_classifier': self.is_classifier,
                'feature_names': self.feature_names,
                'weights': self.weights,
                'bias': self.bias,
                'model': self.model
            }
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, path: str) -> None:
        """
        Load model from file
        
        Args:
            path: Path to load the model from
        """
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model_type = model_data['model_type']
        self.trained = model_data['trained']
        self.is_classifier = model_data['is_classifier']
        self.feature_names = model_data['feature_names']
        self.weights = model_data['weights']
        self.bias = model_data['bias']
        self.model = model_data['model']
        
        logger.info(f"Model loaded from {path}")
    
    def save(self, path: str) -> bool:
        """
        Save model to file (alias for save_model)
        
        Args:
            path: Path to save the model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.save_model(path)
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load(self, path: str) -> bool:
        """
        Load model from file (alias for load_model)
        
        Args:
            path: Path to load the model from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.load_model(path)
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def get_feature_importance(self):
        """
        Get feature importance (for tree-based models)
        
        Returns:
            Array/list of feature importances or None
        """
        if not self.trained:
            return None
        
        if self.model_type in ['random_forest', 'xgboost']:
            if self.model is not None and hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                
                # Return as list for compatibility
                if HAS_NUMPY and isinstance(importances, np.ndarray):
                    return importances.tolist()
                return list(importances) if hasattr(importances, '__iter__') else None
        
        return None
    
    def set_hyperparameters(self, params: Dict = None, **kwargs) -> None:
        """
        Set hyperparameters for the model
        
        Args:
            params: Dictionary of hyperparameters (optional)
            **kwargs: Hyperparameter key-value pairs
        """
        # Store hyperparameters
        if not hasattr(self, 'hyperparameters'):
            self.hyperparameters = {}
        
        # Handle both dict and kwargs
        if params is not None:
            self.hyperparameters.update(params)
        if kwargs:
            self.hyperparameters.update(kwargs)
        
        logger.info(f"Hyperparameters set: {self.hyperparameters}")
    
    def get_hyperparameters(self) -> Dict:
        """
        Get current hyperparameters
        
        Returns:
            Dictionary of hyperparameters
        """
        if hasattr(self, 'hyperparameters'):
            return self.hyperparameters.copy()
        return {}
    
    def cross_validate(self, X, y, cv: int = 5) -> Optional[Dict]:
        """
        Perform cross-validation
        
        Args:
            X: Features
            y: Targets
            cv: Number of cross-validation folds
            
        Returns:
            Dictionary with CV scores or None
        """
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not available for cross-validation")
            return None
        
        if not HAS_NUMPY:
            logger.warning("NumPy not available for cross-validation")
            return None
        
        try:
            # Convert to numpy
            if not isinstance(X, np.ndarray):
                X = np.array(X)
            if not isinstance(y, np.ndarray):
                y = np.array(y)
            
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            
            # Create a temporary model
            if self.model_type == 'random_forest':
                if self.is_classifier:
                    model = RandomForestClassifier(random_state=42)
                else:
                    model = RandomForestRegressor(random_state=42)
            else:
                # Use random forest as default
                model = RandomForestRegressor(random_state=42)
            
            scores = cross_val_score(model, X, y, cv=cv)
            
            return {
                'scores': scores.tolist(),
                'mean': float(np.mean(scores)),
                'std': float(np.std(scores))
            }
        except Exception as e:
            logger.error(f"Cross-validation failed: {e}")
            return None
    
    def grid_search(self, X, y, param_grid: Dict) -> Optional[Dict]:
        """
        Perform grid search for hyperparameters
        
        Args:
            X: Features
            y: Targets
            param_grid: Parameter grid to search
            
        Returns:
            Dictionary with best parameters or None
        """
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not available for grid search")
            return None
        
        if not HAS_NUMPY:
            logger.warning("NumPy not available for grid search")
            return None
        
        try:
            from sklearn.model_selection import GridSearchCV
            
            # Convert to numpy
            if not isinstance(X, np.ndarray):
                X = np.array(X)
            if not isinstance(y, np.ndarray):
                y = np.array(y)
            
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            
            # Create a temporary model
            if self.model_type == 'random_forest':
                if self.is_classifier:
                    model = RandomForestClassifier(random_state=42)
                else:
                    model = RandomForestRegressor(random_state=42)
            else:
                model = RandomForestRegressor(random_state=42)
            
            grid_search = GridSearchCV(model, param_grid, cv=3)
            grid_search.fit(X, y)
            
            return {
                'best_params': grid_search.best_params_,
                'best_score': float(grid_search.best_score_)
            }
        except Exception as e:
            logger.error(f"Grid search failed: {e}")
            return None
    
    def scale_features(self, X, fit: bool = True):
        """
        Scale features using standardization
        
        Args:
            X: Features to scale
            fit: Whether to fit the scaler
            
        Returns:
            Scaled features
        """
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not available for feature scaling")
            return X
        
        if not HAS_NUMPY:
            logger.warning("NumPy not available for feature scaling")
            return X
        
        try:
            from sklearn.preprocessing import StandardScaler
            
            # Convert to numpy
            if not isinstance(X, np.ndarray):
                X = np.array(X)
            
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            
            if fit:
                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X)
            else:
                if hasattr(self, 'scaler'):
                    X_scaled = self.scaler.transform(X)
                else:
                    logger.warning("Scaler not fitted, returning original features")
                    X_scaled = X
            
            return X_scaled
        except Exception as e:
            logger.error(f"Feature scaling failed: {e}")
            return X
