"""
AutoML Pipeline - Automated hyperparameter tuning with Optuna
Provides Bayesian optimization for model hyperparameters
"""
import warnings
from typing import Dict, Any, Callable, Optional
import pandas as pd


class AutoMLPipeline:
    """
    Automated ML pipeline with Optuna for hyperparameter tuning
    Supports Bayesian optimization and automatic feature engineering
    """
    
    def __init__(self, framework: str = 'optuna'):
        """
        Initialize AutoML pipeline
        
        Args:
            framework: Optimization framework to use (default: 'optuna')
        """
        self.framework = framework
        
        # Check if optuna is available
        try:
            import optuna
            self.optuna_available = True
            self.optuna = optuna
        except ImportError:
            self.optuna_available = False
            self.optuna = None
            warnings.warn(
                "optuna library not available. "
                "Install with: pip install optuna"
            )
            
    def _check_availability(self):
        """Check if optuna is available, raise error if not"""
        if not self.optuna_available:
            raise RuntimeError(
                "optuna library not installed. "
                "Install with: pip install optuna"
            )
            
    def tune_hyperparameters(
        self,
        objective_fn: Callable,
        search_space: Dict[str, Any],
        n_trials: int = 100,
        direction: str = 'maximize'
    ) -> Dict[str, Any]:
        """
        Tune hyperparameters using Bayesian optimization
        
        Args:
            objective_fn: Function that takes trial and returns metric value
            search_space: Dictionary defining parameter search space
            n_trials: Number of optimization trials
            direction: Optimization direction ('maximize' or 'minimize')
            
        Returns:
            Dictionary with best_params, best_value, and best_trial
            
        Raises:
            RuntimeError: If optuna not installed
            ValueError: If direction is invalid
        """
        self._check_availability()
        
        if direction not in ['maximize', 'minimize']:
            raise ValueError(
                f"Invalid direction '{direction}'. "
                "Must be 'maximize' or 'minimize'"
            )
            
        try:
            # Create study
            study = self.optuna.create_study(direction=direction)
            
            # Define wrapper for objective function
            def optuna_objective(trial):
                # Suggest parameters based on search space
                params = {}
                for param_name, param_config in search_space.items():
                    param_type = param_config.get('type', 'float')
                    
                    if param_type == 'float':
                        params[param_name] = trial.suggest_float(
                            param_name,
                            param_config.get('low', 0.0),
                            param_config.get('high', 1.0),
                            log=param_config.get('log', False)
                        )
                    elif param_type == 'int':
                        params[param_name] = trial.suggest_int(
                            param_name,
                            param_config.get('low', 0),
                            param_config.get('high', 100)
                        )
                    elif param_type == 'categorical':
                        params[param_name] = trial.suggest_categorical(
                            param_name,
                            param_config.get('choices', [])
                        )
                        
                # Call objective function with suggested parameters
                return objective_fn(params)
                
            # Optimize
            study.optimize(optuna_objective, n_trials=n_trials)
            
            return {
                'best_params': study.best_params,
                'best_value': study.best_value,
                'best_trial': study.best_trial.number,
                'n_trials': n_trials,
                'direction': direction
            }
            
        except Exception as e:
            raise RuntimeError(f"Hyperparameter tuning failed: {e}")
            
    def auto_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Automatic feature engineering on DataFrame
        Creates interaction features, polynomial features, etc.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
            
        # Create copy to avoid modifying original
        df_engineered = df.copy()
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        # Create squared features for numeric columns
        for col in numeric_cols:
            df_engineered[f'{col}_squared'] = df[col] ** 2
            
        # Create interaction features (only for first 5 numeric columns to avoid explosion)
        numeric_cols_subset = numeric_cols[:5]
        for i, col1 in enumerate(numeric_cols_subset):
            for col2 in numeric_cols_subset[i+1:]:
                df_engineered[f'{col1}_{col2}_interaction'] = df[col1] * df[col2]
                
        # Create log features for positive numeric columns
        for col in numeric_cols:
            if (df[col] > 0).all():
                df_engineered[f'{col}_log'] = df[col].apply(lambda x: pd.np.log(x) if x > 0 else 0)
                
        return df_engineered
        
    def is_available(self) -> bool:
        """
        Check if optuna is available
        
        Returns:
            True if optuna is installed, False otherwise
        """
        return self.optuna_available
