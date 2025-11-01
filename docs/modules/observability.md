# Observability Module

The Observability module provides monitoring, metrics, and health tracking for VENOM.

## Components

### Theta Monitor

Real-time system health monitoring based on CPU, memory, and thermal metrics.

```python
from venom.observability import ThetaMonitor
import time

# Initialize monitor
monitor = ThetaMonitor(interval=1.0)

# Start monitoring
monitor.start_monitoring()

# Let it collect metrics
time.sleep(5)

# Get current metrics
metrics = monitor.get_current_metrics()
print(f"System Theta: {metrics['theta']:.3f}")
print(f"CPU Health: {metrics['cpu_health']:.3f}")
print(f"Memory Health: {metrics['memory_health']:.3f}")
print(f"Thermal Health: {metrics['thermal_health']:.3f}")

# Print status
monitor.print_status()

# Stop monitoring
monitor.stop_monitoring()
```

### Prometheus Metrics

Export metrics to Prometheus for monitoring and alerting.

```python
from venom.observability import PrometheusExporter

# Initialize exporter
exporter = PrometheusExporter(port=8000)

# Start metrics server
exporter.start()

# Update metrics
exporter.update_metric('venom_beats_total', 100)
exporter.update_metric('venom_threat_score', 0.25)
exporter.update_metric('venom_pid_error', 0.001)

# Metrics available at http://localhost:8000/metrics
```

### Health Checks

Comprehensive system health monitoring.

```python
from venom.observability import HealthCheck

# Initialize health checker
health = HealthCheck()

# Run checks
results = health.run_checks()

for check in results:
    print(f"{check['name']}: {check['status']}")
    if check['status'] != 'healthy':
        print(f"  Issue: {check['message']}")
```

## CLI Usage

```bash
# Run health check
venom health check

# View metrics
venom health metrics

# Real-time monitoring
venom-omega monitor --duration 30
```

## Theta (θ) Calculation

Theta represents overall system health:

```
θ = 0.3 × H_CPU + 0.3 × H_MEM + 0.4 × H_THERMAL

Where:
  H_CPU = CPU health (0-1)
  H_MEM = Memory health (0-1)  
  H_THERMAL = Thermal health (0-1)
```

Theta values:
- **0.85-1.0**: OPTIMIZE mode (excellent health)
- **0.75-0.85**: BALANCE mode (good health)
- **0.65-0.75**: STABILIZE mode (acceptable)
- **0.50-0.65**: UNWRAP mode (degraded)
- **<0.50**: CRITICAL (needs attention)

## Prometheus Metrics

Available metrics at `http://localhost:8000/metrics`:

- `venom_beats_total`: Total beats executed
- `venom_threat_score`: Current threat score (0-1)
- `venom_pid_error`: PID controller error
- `venom_beat_duration_seconds`: Beat execution time
- `venom_theta`: System health score (0-1)
- `venom_cpu_health`: CPU health score
- `venom_memory_health`: Memory health score
- `venom_thermal_health`: Thermal health score

## Grafana Dashboard

Example dashboard configuration:

```yaml
apiVersion: 1
dashboards:
  - name: VENOM Overview
    panels:
      - title: System Theta
        targets:
          - expr: venom_theta
      - title: Threat Score
        targets:
          - expr: venom_threat_score
      - title: PID Error
        targets:
          - expr: venom_pid_error
      - title: Beat Duration
        targets:
          - expr: rate(venom_beat_duration_seconds[5m])
```

## Configuration

Add to `~/.venomrc`:

```json
{
  "observability": {
    "theta_monitor": {
      "enabled": true,
      "interval": 1.0,
      "weights": {
        "cpu": 0.3,
        "memory": 0.3,
        "thermal": 0.4
      }
    },
    "prometheus": {
      "enabled": true,
      "port": 8000,
      "path": "/metrics"
    },
    "health_checks": {
      "enabled": true,
      "interval": 60
    }
  }
}
```

## Examples

See [examples/observability/](../examples/) for complete examples.

## API Reference

Full API documentation available at [docs/api/observability.md](../api/observability.md).
