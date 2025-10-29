# 4. Скрипт для проверки статуса
#!/bin/bash

# Проверка статуса всех сервисов

GREEN='\\033[0;32m'
RED='\\033[0;31m'
BLUE='\\033[0;34m'
NC='\\033[0m'

check_service() {
    local name=$1
    local url=$2
    local pattern=$3
    
    if curl -s "$url" | grep -q "$pattern" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $name: работает"
        return 0
    else
        echo -e "  ${RED}✗${NC} $name: не доступен"
        return 1
    fi
}

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Статус сервисов мониторинга       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

echo "ELK Stack:"
check_service "Elasticsearch" "http://localhost:9200/_cluster/health" "status"
check_service "Kibana" "http://localhost:5601/api/status" "state"
check_service "Logstash" "http://localhost:9600/_node/stats" "pipeline"

echo ""
echo "Grafana Stack:"
check_service "Prometheus" "http://localhost:9090/-/healthy" "Healthy"
check_service "Node Exporter" "http://localhost:9100/metrics" "node_"
check_service "Grafana" "http://localhost:3000/api/health" "ok"

echo ""
echo -e "${BLUE}Docker контейнеры:${NC}"
docker ps --filter "name=monitoring-" --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"