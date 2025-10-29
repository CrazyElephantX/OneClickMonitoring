# 3. Скрипт для полного удаления
#!/bin/bash

# Полное удаление всех сервисов и данных

RED='\\033[0;31m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

echo -e "${RED}═══════════════════════════════════════════${NC}"
echo -e "${RED}    ВНИМАНИЕ! Это удалит все данные!      ${NC}"
echo -e "${RED}═══════════════════════════════════════════${NC}"
echo ""

read -p "$(echo -e ${YELLOW}Вы уверены? Все дашборды и логи будут удалены! [y/N]: ${NC})" -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Отменено"
    exit 0
fi

echo ""
echo "Удаление контейнеров и volumes..."

# Остановка и удаление ELK
if [ -f "elk-demo/docker-compose.yml" ]; then
    cd elk-demo
    docker-compose down -v
    cd ..
    echo "✓ ELK удален"
fi

# Остановка и удаление Grafana
if [ -f "grafana-demo/docker-compose.yml" ]; then
    cd grafana-demo
    docker-compose down -v
    cd ..
    echo "✓ Grafana удален"
fi

# Удаление директорий (опционально)
read -p "$(echo -e ${YELLOW}Удалить конфигурационные файлы? [y/N]: ${NC})" -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf elk-demo grafana-demo
    echo "✓ Директории удалены"
fi

echo ""
echo "Очистка завершена!"