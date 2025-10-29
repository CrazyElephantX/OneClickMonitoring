# 5. Скрипт для генерации дополнительных логов
#!/bin/bash

# Генерация дополнительных логов для тестирования

GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
NC='\\033[0m'

echo -e "${BLUE}Генерация дополнительных логов...${NC}"

LOG_FILE="elk-demo/sample-logs/generated-$(date +%Y%m%d-%H%M%S).log"

# Генерируем случайные логи
for i in {1..100}; do
    # Случайный IP
    IP="192.168.1.$((RANDOM % 250 + 1))"
    
    # Случайный HTTP метод
    METHODS=("GET" "POST" "PUT" "DELETE")
    METHOD=${METHODS[$RANDOM % ${#METHODS[@]}]}
    
    # Случайный endpoint
    ENDPOINTS=("/api/users" "/api/orders" "/api/products" "/api/login" "/api/dashboard" "/health")
    ENDPOINT=${ENDPOINTS[$RANDOM % ${#ENDPOINTS[@]}]}
    
    # Случайный статус код (с большей вероятностью 200)
    RAND=$((RANDOM % 100))
    if [ $RAND -lt 70 ]; then
        STATUS=200
    elif [ $RAND -lt 85 ]; then
        STATUS=404
    elif [ $RAND -lt 95 ]; then
        STATUS=403
    else
        STATUS=500
    fi
    
    # Случайный размер ответа
    BYTES=$((RANDOM % 10000 + 100))
    
    # Текущее время
    TIMESTAMP=$(date "+%d/%b/%Y:%H:%M:%S %z")
    
    # Формируем строку лога
    echo "$IP - - [$TIMESTAMP] \\"$METHOD $ENDPOINT HTTP/1.1\\" $STATUS $BYTES \\"-\\" \\"Test-Generator/1.0\\"" >> "$LOG_FILE"
    
    # Небольшая задержка для реалистичности
    sleep 0.1
done

echo -e "${GREEN}✓ Создано 100 новых записей в $LOG_FILE${NC}"
echo ""
echo "Для применения перезапустите Logstash:"
echo "  docker restart monitoring-logstash"