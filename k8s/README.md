# Kubernetes Deployment Guide for Portfolio Metrics API

## Prerequisites

- WSL2 with Ubuntu installed
- Docker Desktop running in WSL2
- kind installed in WSL2
- PostgreSQL running on Windows host
- kubectl installed in WSL2

## Architecture Overview

```
Windows Host
├── PostgreSQL (running as Windows service)
└── WSL2 (Ubuntu)
    ├── Docker Daemon
    ├── kind Cluster
    └── Kubernetes Pods
        └── FastAPI Container
            └── Connects to Windows PostgreSQL
```

## Quick Start

For a quick deployment, use the automated script:

```bash
chmod +x k8s/deploy.sh
./k8s/deploy.sh
```

The script will:
1. Check/create secret.yaml
2. Create/check kind cluster
3. Configure database host (Windows IP)
4. Build Docker image
5. Load image into kind
6. Deploy to Kubernetes
7. Optionally start port-forward

See `QUICK_START.md` for more details.

## Manual Deployment Steps

### 1. Get Windows Host IP Address

From WSL2 Ubuntu terminal:

```bash
export WINDOWS_HOST_IP=$(ip route show | grep -i default | awk '{ print $3}')
echo "Windows Host IP: $WINDOWS_HOST_IP"
```

**Note:** In WSL2, Windows host is not `127.0.0.1`, it's a different IP (usually `172.x.x.1`).

### 2. Create Kubernetes Secrets

```bash
# Copy template
cp k8s/secret.yaml.example k8s/secret.yaml

# Edit with your actual values
vim k8s/secret.yaml
```

Required values:
- `DB_PASSWORD`: Your PostgreSQL password
- `SECRET_KEY`: JWT signing key (generate with `openssl rand -hex 32`)

**Important:** `k8s/secret.yaml` is in `.gitignore` - never commit it!

### 3. Update ConfigMap with Windows Host IP

```bash
sed -i "s/host.docker.internal/$WINDOWS_HOST_IP/g" k8s/configmap.yaml
```

### 4. Build and Deploy

```bash
# Build image
docker build -t portfolio-metrics:local .

# Create kind cluster (if not exists)
kind create cluster --name portfolio-metrics

# Load image
kind load docker-image portfolio-metrics:local --name portfolio-metrics

# Deploy
kubectl apply -f k8s/
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n portfolio-metrics

# Check services
kubectl get svc -n portfolio-metrics

# Check logs
kubectl logs -n portfolio-metrics -l app=portfolio-metrics-api
```

## Accessing the Application

### Option 1: Port Forward (Recommended for Development)

```bash
# Use management script
./k8s/port-forward.sh start

# Or manually
kubectl port-forward -n portfolio-metrics svc/portfolio-metrics-api 30080:8000
```

Access at: `http://localhost:30080`

**Port Forward Management:**
```bash
./k8s/port-forward.sh start    # Start
./k8s/port-forward.sh stop     # Stop
./k8s/port-forward.sh status   # Check status
./k8s/port-forward.sh restart  # Restart
```

### Option 2: NodePort

Service is configured with NodePort 30080. However, in kind/WSL2, NodePort may not automatically map to the host. Use port-forward instead.

## Viewing Logs

```bash
# Real-time logs
kubectl logs -n portfolio-metrics -l app=portfolio-metrics-api -f

# Last 50 lines
kubectl logs -n portfolio-metrics -l app=portfolio-metrics-api --tail=50

# Last 10 minutes
kubectl logs -n portfolio-metrics -l app=portfolio-metrics-api --since=10m

# Filter errors only
kubectl logs -n portfolio-metrics -l app=portfolio-metrics-api -f | grep ERROR
```

## Health Checks

Kubernetes automatically performs health checks using probes configured in `deployment.yaml`:

- **Readiness Probe**: Checks every 5 seconds if pod is ready to receive traffic
- **Liveness Probe**: Checks every 10 seconds if pod is still alive (restarts if failed)

This is why you see frequent `/health` endpoint calls in logs. This is normal Kubernetes behavior.

To adjust frequency, edit `deployment.yaml`:
```yaml
readinessProbe:
  periodSeconds: 10  # Change from 5 to 10 seconds

livenessProbe:
  periodSeconds: 30  # Change from 10 to 30 seconds
```

## Service Ports

Port mapping:
```
Browser/Client
    ↓
localhost:30080 (NodePort or Port Forward)
    ↓
Service:8000 (Internal port)
    ↓
Pod:8000 (Container port)
```

**Why 30080?**
- NodePort must be in range 30000-32767 (Kubernetes requirement)
- 30080 = 30000 + 80 (HTTP standard port), easy to remember
- Port-forward can use any port (including 8000), but NodePort cannot

## Troubleshooting

### Pod Cannot Connect to PostgreSQL

1. **Check Windows host IP:**
   ```bash
   ping $WINDOWS_HOST_IP
   ```

2. **Verify PostgreSQL is listening:**
   ```bash
   psql -h $WINDOWS_HOST_IP -U postgres -d user_data
   ```

3. **Check Windows Firewall:**
   - Ensure port 5432 is open
   - Allow connections from WSL2 subnet

4. **Update ConfigMap:**
   ```bash
   kubectl edit configmap portfolio-config -n portfolio-metrics
   ```

### Pod Not Starting

```bash
# Check pod events
kubectl describe pod -n portfolio-metrics -l app=portfolio-metrics-api

# Check logs
kubectl logs -n portfolio-metrics -l app=portfolio-metrics-api

# Check if image is loaded
docker exec -it portfolio-metrics-control-plane crictl images
```

### Cannot Access localhost:30080

**Solution:** Use port-forward instead of NodePort:
```bash
./k8s/port-forward.sh start
```

### Image Pull Errors

```bash
# Reload image
kind load docker-image portfolio-metrics:local --name portfolio-metrics

# Restart deployment
kubectl rollout restart deployment portfolio-metrics-api -n portfolio-metrics
```

## Cleanup

### Stop Port Forward

```bash
./k8s/port-forward.sh stop
# Or
pkill -f "kubectl port-forward"
```

### Delete Kubernetes Resources

```bash
kubectl delete -f k8s/
# Or delete namespace
kubectl delete namespace portfolio-metrics
```

### Delete Kind Cluster

```bash
kind delete cluster --name portfolio-metrics
```

## Updating the Application

```bash
# 1. Rebuild image
docker build -t portfolio-metrics:local .

# 2. Reload into kind
kind load docker-image portfolio-metrics:local --name portfolio-metrics

# 3. Restart deployment
kubectl rollout restart deployment portfolio-metrics-api -n portfolio-metrics

# 4. Watch rollout
kubectl rollout status deployment portfolio-metrics-api -n portfolio-metrics
```

## Important Notes

- **Image Pull Policy**: Set to `Never` because we're using local images
- **NodePort**: Service exposes on port 30080 (configurable)
- **Windows Host IP**: Must be updated in ConfigMap for PostgreSQL connection
- **Secrets**: Never commit `secret.yaml` to git (use `secret.yaml.example`)
- **Port Forward**: Recommended for development, use NodePort/LoadBalancer for production
