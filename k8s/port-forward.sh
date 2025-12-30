#!/bin/bash
# Port forward management script for Portfolio Metrics API

set -e

PORT=30080
SERVICE_NAME="portfolio-metrics-api"
NAMESPACE="portfolio-metrics"
PID_FILE="/tmp/portfolio-metrics-port-forward.pid"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

function start_port_forward() {
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Port forward is already running (PID: $PID)${NC}"
            echo "To stop it, run: ./k8s/port-forward.sh stop"
            return 0
        else
            # PID file exists but process is dead, remove it
            rm -f "$PID_FILE"
        fi
    fi

    # Check if service exists
    if ! kubectl get svc -n "$NAMESPACE" "$SERVICE_NAME" > /dev/null 2>&1; then
        echo -e "${RED}Error: Service $SERVICE_NAME not found in namespace $NAMESPACE${NC}"
        echo "Please deploy the application first using: ./k8s/deploy.sh"
        exit 1
    fi

    echo -e "${YELLOW}Starting port forward...${NC}"
    echo "Forwarding localhost:$PORT -> $SERVICE_NAME:8000"
    
    # Start port-forward in background
    kubectl port-forward -n "$NAMESPACE" svc/"$SERVICE_NAME" "$PORT:8000" > /dev/null 2>&1 &
    PF_PID=$!
    
    # Save PID
    echo $PF_PID > "$PID_FILE"
    
    # Wait a moment to check if it started successfully
    sleep 2
    if ps -p "$PF_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Port forward started successfully (PID: $PF_PID)${NC}"
        echo ""
        echo "Access your API at:"
        echo "  - http://localhost:$PORT/health"
        echo "  - http://localhost:$PORT/api/v1/"
        echo ""
        echo "To stop port forward, run:"
        echo "  ./k8s/port-forward.sh stop"
        echo ""
        echo "To view logs:"
        echo "  kubectl logs -n $NAMESPACE -l app=portfolio-metrics-api -f"
    else
        echo -e "${RED}✗ Failed to start port forward${NC}"
        rm -f "$PID_FILE"
        exit 1
    fi
}

function stop_port_forward() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}Port forward is not running${NC}"
        return 0
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping port forward (PID: $PID)...${NC}"
        kill "$PID" 2>/dev/null || true
        rm -f "$PID_FILE"
        echo -e "${GREEN}✓ Port forward stopped${NC}"
    else
        echo -e "${YELLOW}Port forward process not found, cleaning up PID file${NC}"
        rm -f "$PID_FILE"
    fi
}

function status_port_forward() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}Port forward is not running${NC}"
        return 0
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}Port forward is running (PID: $PID)${NC}"
        echo "Forwarding localhost:$PORT -> $SERVICE_NAME:8000"
    else
        echo -e "${YELLOW}Port forward PID file exists but process is not running${NC}"
        rm -f "$PID_FILE"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        start_port_forward
        ;;
    stop)
        stop_port_forward
        ;;
    status)
        status_port_forward
        ;;
    restart)
        stop_port_forward
        sleep 1
        start_port_forward
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start port forward (default)"
        echo "  stop    - Stop port forward"
        echo "  status  - Check port forward status"
        echo "  restart - Restart port forward"
        exit 1
        ;;
esac

