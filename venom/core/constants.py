"""
Constants for VENOM Λ-GENESIS architecture
"""


class Constants:
    """System-wide constants"""
    
    # Time compression parameters
    T1 = 0.001  # Base time in seconds
    K_FLOWS = 4  # Number of parallel flows
    P_NODES = 5  # Initial number of nodes
    U_BASE = 54.598150033144236  # exp(4)
    T_THRESHOLD = 0.02  # Time threshold for PID
    
    # Stability constants
    EPSILON = 1e-6  # Minimum time value for numerical stability
    EPSILON_RESET = 1e-4  # Error threshold for PID integral reset
    
    # Threat thresholds
    THREAT_QUARANTINE = 0.85
    THREAT_ALERT = 0.60
    
    # Balance thresholds
    STABILITY_THRESHOLD = 0.25
    REPAIR_THRESHOLD = 0.1
    OPT_GAIN_THRESHOLD = 0.1
    
    # PID control limits
    MAX_WEIGHT_DELTA = 0.05  # Maximum weight change per beat
    INTEGRAL_CLAMP_MIN = -1.0  # Anti-windup lower bound
    INTEGRAL_CLAMP_MAX = 1.0  # Anti-windup upper bound
    
    # PID default parameters (from BalanceCore)
    PID_KP = 0.6
    PID_KI = 0.1
    PID_KD = 0.05
    
    # Mesh P2P delays
    MESH_DELAY_HIGH_QUEUE = 0.0003  # 0.3ms when queue > 100
    MESH_DELAY_LOW_QUEUE = 0.001  # 1ms otherwise
    MESH_QUEUE_THRESHOLD = 100
