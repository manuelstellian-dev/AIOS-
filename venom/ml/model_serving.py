"""
Model Serving - REST API for model inference using FastAPI
Provides endpoints for model registration and prediction
"""
import warnings
from typing import Dict, Any, Optional, Callable
import threading


class ModelServer:
    """
    REST API server for ML model inference
    Provides health check, model listing, and prediction endpoints
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8001):
        """
        Initialize model server
        
        Args:
            host: Host to bind server to
            port: Port to bind server to
        """
        self.host = host
        self.port = port
        self._models = {}
        self._preprocessors = {}
        self._server_thread = None
        self._server = None
        
        # Check if FastAPI is available
        try:
            import fastapi
            import uvicorn
            from fastapi import FastAPI, HTTPException
            from pydantic import BaseModel
            
            self.fastapi_available = True
            self.fastapi = fastapi
            self.uvicorn = uvicorn
            self.FastAPI = FastAPI
            self.HTTPException = HTTPException
            self.BaseModel = BaseModel
            
        except ImportError:
            self.fastapi_available = False
            self.fastapi = None
            self.uvicorn = None
            self.FastAPI = None
            self.HTTPException = None
            self.BaseModel = None
            warnings.warn(
                "fastapi/uvicorn not available. "
                "Install with: pip install fastapi uvicorn"
            )
            
    def _check_availability(self):
        """Check if FastAPI is available, raise error if not"""
        if not self.fastapi_available:
            raise RuntimeError(
                "fastapi/uvicorn not installed. "
                "Install with: pip install fastapi uvicorn"
            )
            
    def register_model(self, name: str, model: Any, 
                      preprocessor: Optional[Callable] = None):
        """
        Register a model for serving
        
        Args:
            name: Model name
            model: Model object (must have predict method or be callable)
            preprocessor: Optional preprocessing function
        """
        self._models[name] = model
        if preprocessor is not None:
            self._preprocessors[name] = preprocessor
            
    def _create_app(self):
        """Create FastAPI application with endpoints"""
        self._check_availability()
        
        app = self.FastAPI(title="VENOM Model Server", version="1.0.0")
        
        # Define request/response models
        class PredictRequest(self.BaseModel):
            data: Any
            
        class BatchPredictRequest(self.BaseModel):
            data: list
            
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "models_loaded": len(self._models),
                "host": self.host,
                "port": self.port
            }
            
        @app.get("/models")
        async def list_models():
            """List all registered models"""
            return {
                "models": list(self._models.keys()),
                "count": len(self._models)
            }
            
        @app.post("/predict/{model_name}")
        async def predict(model_name: str, request: PredictRequest):
            """Single prediction endpoint"""
            if model_name not in self._models:
                raise self.HTTPException(
                    status_code=404,
                    detail=f"Model '{model_name}' not found"
                )
                
            model = self._models[model_name]
            data = request.data
            
            # Apply preprocessor if available
            if model_name in self._preprocessors:
                try:
                    data = self._preprocessors[model_name](data)
                except Exception as e:
                    raise self.HTTPException(
                        status_code=400,
                        detail=f"Preprocessing failed: {str(e)}"
                    )
                    
            # Run prediction
            try:
                if hasattr(model, 'predict'):
                    prediction = model.predict(data)
                elif callable(model):
                    prediction = model(data)
                else:
                    raise self.HTTPException(
                        status_code=500,
                        detail="Model does not have predict method or is not callable"
                    )
                    
                return {
                    "model": model_name,
                    "prediction": prediction,
                    "status": "success"
                }
                
            except Exception as e:
                raise self.HTTPException(
                    status_code=500,
                    detail=f"Prediction failed: {str(e)}"
                )
                
        @app.post("/batch_predict/{model_name}")
        async def batch_predict(model_name: str, request: BatchPredictRequest):
            """Batch prediction endpoint"""
            if model_name not in self._models:
                raise self.HTTPException(
                    status_code=404,
                    detail=f"Model '{model_name}' not found"
                )
                
            model = self._models[model_name]
            data_list = request.data
            
            predictions = []
            for data in data_list:
                # Apply preprocessor if available
                if model_name in self._preprocessors:
                    try:
                        data = self._preprocessors[model_name](data)
                    except Exception as e:
                        predictions.append({
                            "error": f"Preprocessing failed: {str(e)}"
                        })
                        continue
                        
                # Run prediction
                try:
                    if hasattr(model, 'predict'):
                        prediction = model.predict(data)
                    elif callable(model):
                        prediction = model(data)
                    else:
                        predictions.append({
                            "error": "Model does not have predict method or is not callable"
                        })
                        continue
                        
                    predictions.append(prediction)
                    
                except Exception as e:
                    predictions.append({
                        "error": f"Prediction failed: {str(e)}"
                    })
                    
            return {
                "model": model_name,
                "predictions": predictions,
                "count": len(predictions),
                "status": "success"
            }
            
        return app
        
    def start(self):
        """Start the model server"""
        self._check_availability()
        
        if self._server_thread is not None and self._server_thread.is_alive():
            warnings.warn("Server is already running")
            return
            
        app = self._create_app()
        
        # Create server configuration
        config = self.uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        self._server = self.uvicorn.Server(config)
        
        # Run server in separate thread
        self._server_thread = threading.Thread(
            target=self._server.run,
            daemon=True
        )
        self._server_thread.start()
        
    def stop(self):
        """Stop the model server"""
        if self._server is not None:
            self._server.should_exit = True
            if self._server_thread is not None:
                self._server_thread.join(timeout=5.0)
            self._server = None
            self._server_thread = None
            
    def is_available(self) -> bool:
        """
        Check if FastAPI is available
        
        Returns:
            True if fastapi/uvicorn installed, False otherwise
        """
        return self.fastapi_available
        
    def is_running(self) -> bool:
        """
        Check if server is running
        
        Returns:
            True if server thread is alive, False otherwise
        """
        return (self._server_thread is not None and 
                self._server_thread.is_alive())
