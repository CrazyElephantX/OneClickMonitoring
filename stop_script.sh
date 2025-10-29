# 2. Скрипт для остановки всех сервисов
#!/bin/bash

# Остановка всех сервисов мониторинга

RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

echo -e "${YELLOW}Остановка сервисов...${NC}"
echo ""

# Остановка ELK
if [ -f "elk-demo/docker-compose.yml" ]; then
    echo "Остановка ELK стека..."
    cd elk-demo
    docker-compose down
    cd ..
    echo -e "${GREEN}✓ ELK остановлен${NC}"
else
    echo -e "${RED}✗ ELK конфигурация не найдена${NC}"
fi

echo ""

# Остановка Grafana
if [ -f "grafana-demo/docker-compose.yml" ]; then
    echo "Остановка Grafana стека..."
    cd grafana-demo
    docker-compose down
    cd ..
    echo -e "${GREEN}✓ Grafana остановлен${NC}"
else
    echo -e "${RED}✗ Grafana конфигурация не найдена${NC}"
fi

echo ""
echo -e "${GREEN}Все сервисы остановлены!${NC}"