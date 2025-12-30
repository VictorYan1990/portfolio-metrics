#!/bin/bash
# Quick deployment script for kind cluster

set -e  # Exit on error

echo "🚀 Portfolio Metrics API - Kind Deployment Script"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if secret.yaml exists
echo -e "${YELLOW}Step 1: Checking secrets...${NC}"
if [ ! -f "k8s/secret.yaml" ]; then
    echo -e "${YELLOW}Warning: k8s/secret.yaml not found${NC}"
    echo "Creating from template..."
    cp k8s/secret.yaml.example k8s/secret.yaml
    echo -e "${RED}Please edit k8s/secret.yaml with your actual values before continuing!${NC}"
    echo "Press Enter after editing..."
    read
fi

# Step 2: Check if kind cluster exists (needed to test host.docker.internal)
echo -e "${YELLOW}Step 2: Checking kind cluster...${NC}"
if ! kind get clusters | grep -q "portfolio-metrics"; then
    echo "Creating kind cluster..."
    kind create cluster --name portfolio-metrics
    echo -e "${GREEN}Kind cluster created${NC}"
else
    echo -e "${GREEN}Kind cluster already exists${NC}"
fi

# Step 3: Configure DB_HOST - try host.docker.internal first, fallback to Windows IP
echo -e "${YELLOW}Step 3: Configuring database host...${NC}"
# Try to resolve host.docker.internal from kind node
# Note: kind may not support host.docker.internal by default
# If it doesn't work, we'll use the Windows host IP
if docker exec portfolio-metrics-control-plane sh -c "getent hosts host.docker.internal" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ host.docker.internal is supported in kind cluster${NC}"
    echo -e "${GREEN}ConfigMap will use host.docker.internal${NC}"
    # Ensure configmap uses host.docker.internal (restore if modified)
    if grep -q "DB_HOST.*172\." k8s/configmap.yaml 2>/dev/null; then
        sed -i "s/DB_HOST: \".*\"/DB_HOST: \"host.docker.internal\"/" k8s/configmap.yaml
    fi
else
    echo -e "${YELLOW}host.docker.internal not supported, using Windows host IP...${NC}"
    WINDOWS_HOST_IP=$(ip route show | grep -i default | awk '{ print $3}')
    if [ -z "$WINDOWS_HOST_IP" ]; then
        echo -e "${RED}Error: Could not determine Windows host IP${NC}"
        echo -e "${YELLOW}Note: In WSL2, Windows host is not 127.0.0.1, it's a different IP (usually 172.x.x.1)${NC}"
        exit 1
    fi
    echo -e "${GREEN}Windows Host IP: $WINDOWS_HOST_IP${NC}"
    echo -e "${YELLOW}Updating ConfigMap with Windows host IP...${NC}"
    sed -i "s/host.docker.internal/$WINDOWS_HOST_IP/g" k8s/configmap.yaml
    echo -e "${GREEN}ConfigMap updated${NC}"
fi

# Step 4: Build Docker image
echo -e "${YELLOW}Step 4: Building Docker image...${NC}"
docker build -t portfolio-metrics:local .
echo -e "${GREEN}Image built successfully${NC}"

# Step 5: Load image into kind
echo -e "${YELLOW}Step 5: Loading image into kind cluster...${NC}"
kind load docker-image portfolio-metrics:local --name portfolio-metrics
echo -e "${GREEN}Image loaded into kind${NC}"

# Step 6: Apply Kubernetes manifests
echo -e "${YELLOW}Step 6: Applying Kubernetes manifests...${NC}"
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
echo -e "${GREEN}Manifests applied${NC}"

# Step 7: Wait for deployment
echo -e "${YELLOW}Step 7: Waiting for deployment to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/portfolio-metrics-api -n portfolio-metrics
echo -e "${GREEN}Deployment ready!${NC}"

# Step 8: Show status
echo -e "${YELLOW}Step 8: Deployment status:${NC}"
kubectl get pods -n portfolio-metrics
kubectl get svc -n portfolio-metrics

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

# Step 9: Optionally start port-forward
echo -e "${YELLOW}Step 9: Port forwarding setup...${NC}"
if [ -t 0 ]; then
    # Interactive mode - ask user
    echo "Do you want to start port-forward? (y/n)"
    read -t 10 -p "Press Enter for 'yes' or wait 10 seconds: " START_PF || START_PF="y"
else
    # Non-interactive mode - skip
    START_PF="n"
fi

if [[ "$START_PF" =~ ^[Yy]$ ]] || [[ -z "$START_PF" ]]; then
    echo -e "${YELLOW}Starting port-forward...${NC}"
    chmod +x k8s/port-forward.sh 2>/dev/null || true
    ./k8s/port-forward.sh start
else
    echo -e "${YELLOW}Skipping port-forward${NC}"
    echo ""
    echo "To start port-forward later, run:"
    echo "  ./k8s/port-forward.sh start"
fi

echo ""
echo "Access your API at:"
echo "  - http://localhost:30080/health"
echo "  - http://localhost:30080/api/v1/"
echo ""
echo "Useful commands:"
echo "  View logs:    kubectl logs -n portfolio-metrics -l app=portfolio-metrics-api -f"
echo "  Stop PF:      ./k8s/port-forward.sh stop"
echo "  Status PF:    ./k8s/port-forward.sh status"
echo "  Delete all:   kubectl delete -f k8s/"

