# Quick Start Guide - Kind Deployment

## Prerequisites Check

```bash
# In WSL2 Ubuntu terminal, verify:
docker --version
kind --version
kubectl version --client
```

## One-Command Deployment (Recommended)

```bash
# Make script executable (if not already)
chmod +x k8s/deploy.sh

# Run deployment script
./k8s/deploy.sh
```

The script will:
1. ✅ Get Windows host IP automatically
2. ✅ Build Docker image
3. ✅ Create/use kind cluster
4. ✅ Load image into kind
5. ✅ Deploy to Kubernetes
6. ✅ Wait for readiness
7. ✅ Optionally start port-forward (prompts for confirmation)

## Manual Deployment (Step-by-Step)

### 1. Get Windows Host IP

```bash
export WINDOWS_HOST_IP=$(ip route show | grep -i default | awk '{ print $3}')
echo $WINDOWS_HOST_IP  # Should be something like 172.x.x.1
```

### 2. Create Secret File

```bash
cp k8s/secret.yaml.example k8s/secret.yaml
# Edit k8s/secret.yaml with your actual values
vim k8s/secret.yaml
```

### 3. Update ConfigMap

```bash
# Replace host.docker.internal with Windows host IP
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

### 5. Start Port Forward (if using port-forward instead of NodePort)

```bash
# Start port-forward
chmod +x k8s/port-forward.sh
./k8s/port-forward.sh start

# Or manually
kubectl port-forward -n portfolio-metrics svc/portfolio-metrics-api 30080:8000
```

### 6. Verify

```bash
# Check pods
kubectl get pods -n portfolio-metrics

# Check logs
kubectl logs -n portfolio-metrics -l app=portfolio-metrics-api

# Test API (if port-forward is running)
curl http://localhost:30080/health
```

## Port Forward Management

The `port-forward.sh` script provides easy management of port forwarding:

```bash
# Start port-forward
./k8s/port-forward.sh start

# Check status
./k8s/port-forward.sh status

# Stop port-forward
./k8s/port-forward.sh stop

# Restart port-forward
./k8s/port-forward.sh restart
```

## Troubleshooting

### Cannot Connect to PostgreSQL

```bash
# Test connection from WSL2
psql -h $WINDOWS_HOST_IP -U postgres -d user_data

# If fails, check Windows Firewall allows port 5432
# Update PostgreSQL pg_hba.conf to allow WSL2 subnet
```

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod -n portfolio-metrics -l app=portfolio-metrics-api

# Check events
kubectl get events -n portfolio-metrics --sort-by='.lastTimestamp'
```

### Image Not Found

```bash
# Reload image
kind load docker-image portfolio-metrics:local --name portfolio-metrics

# Restart deployment
kubectl rollout restart deployment portfolio-metrics-api -n portfolio-metrics
```

## Access Points

- **API Health**: http://localhost:30080/health
- **API Docs**: http://localhost:30080/docs
- **API Root**: http://localhost:30080/api/v1/

## Cleanup

```bash
# Delete everything
kubectl delete -f k8s/
kind delete cluster --name portfolio-metrics
```

