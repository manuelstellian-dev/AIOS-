"""
VENOM Stream Processor - Real-time stream processing with windowing
Provides sliding/tumbling windows, aggregations, and real-time statistics
"""

import logging
import time
from typing import List, Dict, Callable, Optional, Any
from collections import deque
import statistics

logger = logging.getLogger(__name__)


class StreamProcessor:
    """
    Real-time stream processor with advanced windowing capabilities
    Supports sliding and tumbling windows with multiple aggregation functions
    """
    
    def __init__(self, window_size: int = 100, window_type: str = 'sliding'):
        """
        Initialize stream processor
        
        Args:
            window_size: Size of the window (number of events or time-based)
            window_type: Type of window ('sliding' or 'tumbling')
        """
        if window_type not in ['sliding', 'tumbling']:
            raise ValueError(f"window_type must be 'sliding' or 'tumbling', got '{window_type}'")
        
        self.window_size = window_size
        self.window_type = window_type
        self.events: deque = deque(maxlen=window_size if window_type == 'sliding' else None)
        self.tumbling_buffer: List[Dict] = [] if window_type == 'tumbling' else None
        self.total_events = 0
        self.total_windows = 0
        self.start_time = time.time()
        
        logger.info(f"StreamProcessor initialized: window_size={window_size}, window_type={window_type}")
    
    def add_event(self, event: Dict) -> None:
        """
        Add an event to the stream
        
        Args:
            event: Event dictionary to add
        """
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = time.time()
        
        self.total_events += 1
        
        if self.window_type == 'sliding':
            self.events.append(event)
        else:  # tumbling
            self.tumbling_buffer.append(event)
            
            # Check if window is full
            if len(self.tumbling_buffer) >= self.window_size:
                # Process window
                self.events = deque(self.tumbling_buffer)
                self.tumbling_buffer = []
                self.total_windows += 1
    
    def get_window(self) -> List[Dict]:
        """
        Get current window events
        
        Returns:
            List of events in current window
        """
        if self.window_type == 'sliding':
            return list(self.events)
        else:  # tumbling
            return self.tumbling_buffer if self.tumbling_buffer else list(self.events)
    
    def aggregate(self, metric: str, func: str = 'mean') -> float:
        """
        Aggregate a metric across the window
        
        Args:
            metric: Name of the metric field to aggregate
            func: Aggregation function ('mean', 'sum', 'count', 'min', 'max', 'std')
            
        Returns:
            Aggregated value
        """
        window = self.get_window()
        
        if not window:
            return 0.0
        
        # Extract metric values
        values = []
        for event in window:
            if metric in event and isinstance(event[metric], (int, float)):
                values.append(float(event[metric]))
        
        if not values:
            return 0.0
        
        # Apply aggregation function
        if func == 'mean':
            return statistics.mean(values)
        elif func == 'sum':
            return sum(values)
        elif func == 'count':
            return float(len(values))
        elif func == 'min':
            return min(values)
        elif func == 'max':
            return max(values)
        elif func == 'std':
            return statistics.stdev(values) if len(values) > 1 else 0.0
        else:
            raise ValueError(f"Unknown aggregation function: {func}")
    
    def filter(self, predicate: Callable[[Dict], bool]) -> List[Dict]:
        """
        Filter events in the window
        
        Args:
            predicate: Function that returns True for events to keep
            
        Returns:
            Filtered list of events
        """
        window = self.get_window()
        return [event for event in window if predicate(event)]
    
    def group_by(self, key: str) -> Dict[str, List[Dict]]:
        """
        Group events by a key field
        
        Args:
            key: Field name to group by
            
        Returns:
            Dictionary mapping key values to lists of events
        """
        window = self.get_window()
        groups: Dict[str, List[Dict]] = {}
        
        for event in window:
            if key in event:
                group_key = str(event[key])
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(event)
        
        return groups
    
    def compute_statistics(self) -> Dict[str, float]:
        """
        Compute real-time statistics about the stream
        
        Returns:
            Dictionary with throughput, latency percentiles, and other stats
        """
        window = self.get_window()
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        stats = {
            'total_events': float(self.total_events),
            'window_size': float(len(window)),
            'throughput': self.total_events / elapsed_time if elapsed_time > 0 else 0.0,
            'elapsed_time': elapsed_time
        }
        
        # Calculate latency if timestamps available
        if window:
            latencies = []
            for event in window:
                if 'timestamp' in event and 'processed_time' in event:
                    latency = event['processed_time'] - event['timestamp']
                    latencies.append(latency)
            
            if latencies:
                sorted_latencies = sorted(latencies)
                n = len(sorted_latencies)
                stats['latency_mean'] = statistics.mean(sorted_latencies)
                stats['latency_median'] = sorted_latencies[n // 2]
                stats['latency_p95'] = sorted_latencies[int(n * 0.95)] if n > 1 else sorted_latencies[0]
                stats['latency_p99'] = sorted_latencies[int(n * 0.99)] if n > 1 else sorted_latencies[0]
        
        return stats
    
    def reset(self) -> None:
        """Reset the stream processor state"""
        self.events.clear()
        if self.tumbling_buffer is not None:
            self.tumbling_buffer = []
        self.total_events = 0
        self.total_windows = 0
        self.start_time = time.time()
        logger.info("StreamProcessor reset")
