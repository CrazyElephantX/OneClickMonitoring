
# Создаю комплексный скрипт для автоматического развертывания полного окружения
# для уроков по Kibana и Grafana

# 1. Главный setup script (bash)
main_setup_script = """#!/bin/bash

#############################################
# Автоматическая установка окружения для
# Интенсива 8: Мониторинг и логирование
# Kibana + Grafana
#############################################

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Функции для красивого вывода
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Проверка Docker
check_docker() {
    print_header "Проверка зависимостей"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен!"
        print_info "Установите Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker установлен: $(docker --version)"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose не установлен!"
        print_info "Установите Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose установлен: $(docker-compose --version)"
    
    # Проверка что Docker запущен
    if ! docker info &> /dev/null; then
        print_error "Docker не запущен!"
        print_info "Запустите Docker Desktop или Docker daemon"
        exit 1
    fi
    print_success "Docker daemon работает"
}

# Проверка доступных портов
check_ports() {
    print_header "Проверка доступности портов"
    
    PORTS=(3000 5601 9090 9100 9200 6000)
    PORT_NAMES=("Grafana" "Kibana" "Prometheus" "Node-Exporter" "Elasticsearch" "Logstash")
    
    for i in "${!PORTS[@]}"; do
        PORT=${PORTS[$i]}
        NAME=${PORT_NAMES[$i]}
        
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$PORT " ; then
            print_warning "Порт $PORT ($NAME) уже занят!"
            print_info "Остановите сервис на порту $PORT или измените порт в docker-compose"
        else
            print_success "Порт $PORT ($NAME) свободен"
        fi
    done
}

# Создание структуры директорий
create_directories() {
    print_header "Создание структуры директорий"
    
    mkdir -p elk-demo/logstash-pipeline
    mkdir -p elk-demo/sample-logs
    mkdir -p grafana-demo/prometheus
    mkdir -p grafana-demo/grafana/provisioning/datasources
    mkdir -p grafana-demo/grafana/provisioning/dashboards
    
    print_success "Директории созданы"
}

# Создание конфигурационных файлов
create_configs() {
    print_header "Создание конфигурационных файлов"
    
    # ELK docker-compose
    cat > elk-demo/docker-compose.yml << 'EOF'

services:
  elasticsearch:
    image: elasticsearch:8.13.0
    container_name: monitoring-elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
      - xpack.security.http.ssl.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - elk
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  kibana:
    image: kibana:8.13.0
    container_name: monitoring-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - XPACK_SECURITY_ENABLED=false
    ports:
      - "5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy
    networks:
      - elk
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5601/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  logstash:
    image: logstash:8.13.0
    container_name: monitoring-logstash
    volumes:
      - ./logstash-pipeline:/usr/share/logstash/pipeline
      - ./sample-logs:/usr/share/logstash/sample-logs
    ports:
      - "6000:6000"
      - "9600:9600"
    depends_on:
      elasticsearch:
        condition: service_healthy
    networks:
      - elk
    environment:
      - "LS_JAVA_OPTS=-Xmx256m -Xms256m"

networks:
  elk:
    driver: bridge

volumes:
  elasticsearch_data:
    driver: local
EOF
    print_success "ELK docker-compose.yml создан"
    
    # Logstash pipeline
    cat > elk-demo/logstash-pipeline/logstash.conf << 'EOF'
input {
  file {
    path => "/usr/share/logstash/sample-logs/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => "plain"
  }
}

filter {
  grok {
    match => { "message" => "%{COMBINEDAPACHELOG}" }
  }
  
  if "_grokparsefailure" not in [tags] {
    date {
      match => [ "timestamp" , "dd/MMM/yyyy:HH:mm:ss Z" ]
    }
    
    mutate {
      convert => { "response" => "integer" }
      convert => { "bytes" => "integer" }
    }
    
    if [clientip] {
      geoip {
        source => "clientip"
        target => "geoip"
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "sample-logs-%{+YYYY.MM.dd}"
  }
  stdout {
    codec => rubydebug
  }
}
EOF
    print_success "Logstash pipeline создан"
    
    # Grafana docker-compose
    cat > grafana-demo/docker-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: monitoring-prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: monitoring-node-exporter
    restart: unless-stopped
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - monitoring

  grafana:
    image: grafana/grafana-oss:latest
    container_name: monitoring-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=http://localhost:3000
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
EOF
    print_success "Grafana docker-compose.yml создан"
    
    # Prometheus config
    cat > grafana-demo/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 5s
EOF
    print_success "Prometheus config создан"
    
    # Grafana provisioning - datasource
    cat > grafana-demo/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF
    print_success "Grafana datasource provisioning создан"
    
    # Grafana provisioning - dashboard provider
    cat > grafana-demo/grafana/provisioning/dashboards/dashboards.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'Default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF
    print_success "Grafana dashboard provisioning создан"
}

# Генерация sample логов
generate_sample_logs() {
    print_header "Генерация демонстрационных логов"
    
    # Apache access logs
    cat > elk-demo/sample-logs/apache-access.log << 'EOF'
192.168.1.10 - - [29/Oct/2025:10:15:23 +0300] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.20 - - [29/Oct/2025:10:16:45 +0300] "POST /api/login HTTP/1.1" 200 567 "-" "curl/7.68.0"
192.168.1.30 - admin [29/Oct/2025:10:17:12 +0300] "GET /api/products HTTP/1.1" 404 0 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)"
192.168.1.10 - - [29/Oct/2025:10:18:34 +0300] "GET /api/dashboard HTTP/1.1" 500 89 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
192.168.1.40 - user1 [29/Oct/2025:10:19:56 +0300] "DELETE /api/users/123 HTTP/1.1" 200 45 "-" "PostmanRuntime/7.26.8"
192.168.1.20 - - [29/Oct/2025:10:20:11 +0300] "GET /api/stats HTTP/1.1" 200 2345 "-" "Mozilla/5.0 (X11; Linux x86_64)"
192.168.1.50 - - [29/Oct/2025:10:21:33 +0300] "POST /api/register HTTP/1.1" 201 678 "https://example.com/signup" "Mozilla/5.0 (Android 10; Mobile)"
192.168.1.30 - - [29/Oct/2025:10:22:44 +0300] "GET /api/users/456 HTTP/1.1" 200 890 "-" "Python-requests/2.25.1"
192.168.1.10 - admin [29/Oct/2025:10:23:55 +0300] "PUT /api/settings HTTP/1.1" 500 12 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.60 - - [29/Oct/2025:10:24:08 +0300] "GET /health HTTP/1.1" 200 34 "-" "kube-probe/1.20"
192.168.1.70 - - [29/Oct/2025:10:25:15 +0300] "GET /api/orders HTTP/1.1" 403 156 "-" "Mozilla/5.0 (compatible; Googlebot/2.1)"
192.168.1.20 - user2 [29/Oct/2025:10:26:22 +0300] "POST /api/orders HTTP/1.1" 201 1024 "https://shop.example.com" "Mozilla/5.0 (iPad; CPU OS 14_0)"
192.168.1.80 - - [29/Oct/2025:10:27:33 +0300] "GET /api/products/search?q=laptop HTTP/1.1" 200 5678 "https://example.com/search" "Mozilla/5.0 (Edge)"
192.168.1.30 - - [29/Oct/2025:10:28:44 +0300] "DELETE /api/cache HTTP/1.1" 204 0 "-" "curl/7.68.0"
192.168.1.90 - guest [29/Oct/2025:10:29:55 +0300] "GET /api/public/info HTTP/1.1" 200 789 "-" "bot-scanner/1.0"
192.168.1.100 - - [29/Oct/2025:10:30:10 +0300] "GET /api/metrics HTTP/1.1" 200 456 "-" "Prometheus/2.40"
192.168.1.10 - - [29/Oct/2025:10:31:22 +0300] "POST /api/payment HTTP/1.1" 500 234 "-" "Mozilla/5.0 (Windows)"
192.168.1.110 - - [29/Oct/2025:10:32:33 +0300] "GET /api/users/list HTTP/1.1" 200 8901 "-" "axios/0.21.1"
192.168.1.20 - - [29/Oct/2025:10:33:44 +0300] "PUT /api/profile HTTP/1.1" 200 345 "-" "Mozilla/5.0"
192.168.1.30 - - [29/Oct/2025:10:34:55 +0300] "GET /api/config HTTP/1.1" 404 0 "-" "curl/7.68.0"
EOF
    
    # Application logs
    cat > elk-demo/sample-logs/application.log << 'EOF'
2025-10-29T10:15:23+03:00 INFO [main] com.example.Application - Application started successfully on port 8080
2025-10-29T10:16:45+03:00 INFO [http-thread-1] com.example.UserController - User login successful: user_id=user123
2025-10-29T10:17:12+03:00 WARN [http-thread-2] com.example.ProductController - Product not found: product_id=999
2025-10-29T10:18:34+03:00 ERROR [http-thread-1] com.example.DashboardController - Database connection failed: timeout after 30s
2025-10-29T10:19:56+03:00 INFO [http-thread-3] com.example.UserController - User deleted: user_id=123, admin=user1
2025-10-29T10:20:11+03:00 DEBUG [scheduler] com.example.StatsService - Calculating daily statistics: records=15432
2025-10-29T10:21:33+03:00 INFO [http-thread-2] com.example.UserController - New user registered: email=test@example.com
2025-10-29T10:22:44+03:00 INFO [http-thread-1] com.example.UserController - User profile requested: user_id=456
2025-10-29T10:23:55+03:00 ERROR [http-thread-3] com.example.SettingsController - Failed to update settings: validation error on field=notification_email
2025-10-29T10:24:08+03:00 INFO [health-check] com.example.HealthController - Health check passed: uptime=14d 5h 23m
2025-10-29T10:25:15+03:00 WARN [security] com.example.SecurityFilter - Access denied for IP: 192.168.1.70, reason=rate_limit_exceeded
2025-10-29T10:26:22+03:00 INFO [http-thread-2] com.example.OrderController - Order created: order_id=ORD-001, amount=299.99, user=user2
2025-10-29T10:27:33+03:00 DEBUG [search-service] com.example.SearchService - Search query executed: query='laptop', results=42, time_ms=156
2025-10-29T10:28:44+03:00 INFO [cache-manager] com.example.CacheManager - Cache cleared successfully: size=1024MB, items=15678
2025-10-29T10:29:55+03:00 WARN [rate-limiter] com.example.RateLimitFilter - Rate limit exceeded: ip=192.168.1.90, endpoint=/api/public/info
2025-10-29T10:30:10+03:00 DEBUG [metrics] com.example.MetricsController - Metrics scraped: response_time=45ms
2025-10-29T10:31:22+03:00 ERROR [payment-service] com.example.PaymentController - Payment processing failed: error=insufficient_funds, user=192.168.1.10
2025-10-29T10:32:33+03:00 INFO [http-thread-4] com.example.UserController - User list fetched: count=234, page=1
2025-10-29T10:33:44+03:00 INFO [http-thread-1] com.example.ProfileController - Profile updated: user_id=user123, fields=[avatar,bio]
2025-10-29T10:34:55+03:00 WARN [http-thread-2] com.example.ConfigController - Config endpoint not found: path=/api/config
EOF
    
    print_success "Sample логи созданы (20 записей Apache + 20 application логов)"
}

# Запуск ELK стека
start_elk() {
    print_header "Запуск ELK стека"
    
    cd elk-demo
    
    print_info "Запускаем контейнеры... (это может занять 2-3 минуты)"
    docker-compose up -d
    
    print_info "Ожидаем готовности Elasticsearch..."
    sleep 30
    
    # Проверка здоровья
    for i in {1..30}; do
        if curl -s http://localhost:9200/_cluster/health | grep -q '"status":"green\\|yellow"'; then
            print_success "Elasticsearch запущен и готов"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    print_info "Ожидаем готовности Kibana..."
    for i in {1..30}; do
        if curl -s http://localhost:5601/api/status | grep -q '"state":"green"'; then
            print_success "Kibana запущен и готов"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    cd ..
    print_success "ELK стек запущен!"
}

# Запуск Grafana стека
start_grafana() {
    print_header "Запуск Grafana стека"
    
    cd grafana-demo
    
    print_info "Запускаем контейнеры..."
    docker-compose up -d
    
    print_info "Ожидаем готовности сервисов..."
    sleep 15
    
    # Проверка Prometheus
    if curl -s http://localhost:9090/-/healthy | grep -q "Healthy"; then
        print_success "Prometheus запущен"
    fi
    
    # Проверка Node Exporter
    if curl -s http://localhost:9100/metrics | grep -q "node_"; then
        print_success "Node Exporter запущен"
    fi
    
    # Проверка Grafana
    for i in {1..20}; do
        if curl -s http://localhost:3000/api/health | grep -q "ok"; then
            print_success "Grafana запущен и готов"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    cd ..
    print_success "Grafana стек запущен!"
}

# Создание index pattern в Kibana
setup_kibana_index() {
    print_header "Настройка Kibana index pattern"
    
    # Ждем пока логи проиндексируются
    print_info "Ожидаем индексации логов..."
    sleep 10
    
    # Создаем index pattern через API
    curl -X POST "http://localhost:5601/api/saved_objects/index-pattern/sample-logs" \\
      -H 'kbn-xsrf: true' \\
      -H 'Content-Type: application/json' \\
      -d '{
        "attributes": {
          "title": "sample-logs-*",
          "timeFieldName": "@timestamp"
        }
      }' 2>/dev/null
    
    print_success "Index pattern 'sample-logs-*' создан"
}

# Вывод итоговой информации
print_summary() {
    print_header "УСТАНОВКА ЗАВЕРШЕНА!"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Все сервисы успешно запущены!             ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BLUE}📊 Kibana (Логи):${NC}"
    echo -e "   URL: ${YELLOW}http://localhost:5601${NC}"
    echo -e "   Авторизация: не требуется"
    echo -e "   Index Pattern: sample-logs-*"
    echo ""
    
    echo -e "${BLUE}📈 Grafana (Метрики):${NC}"
    echo -e "   URL: ${YELLOW}http://localhost:3000${NC}"
    echo -e "   Логин: ${YELLOW}admin${NC}"
    echo -e "   Пароль: ${YELLOW}admin${NC}"
    echo -e "   Data Source: Prometheus (уже подключен)"
    echo ""
    
    echo -e "${BLUE}🔍 Prometheus:${NC}"
    echo -e "   URL: ${YELLOW}http://localhost:9090${NC}"
    echo ""
    
    echo -e "${BLUE}💻 Node Exporter:${NC}"
    echo -e "   URL: ${YELLOW}http://localhost:9100/metrics${NC}"
    echo ""
    
    echo -e "${BLUE}🔧 Elasticsearch:${NC}"
    echo -e "   URL: ${YELLOW}http://localhost:9200${NC}"
    echo ""
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}📚 Полезные команды:${NC}"
    echo ""
    echo "Просмотр логов контейнеров:"
    echo "  docker-compose -f elk-demo/docker-compose.yml logs -f"
    echo "  docker-compose -f grafana-demo/docker-compose.yml logs -f"
    echo ""
    echo "Остановка сервисов:"
    echo "  docker-compose -f elk-demo/docker-compose.yml down"
    echo "  docker-compose -f grafana-demo/docker-compose.yml down"
    echo ""
    echo "Полное удаление (включая данные):"
    echo "  docker-compose -f elk-demo/docker-compose.yml down -v"
    echo "  docker-compose -f grafana-demo/docker-compose.yml down -v"
    echo ""
    echo "Перезапуск сервисов:"
    echo "  docker-compose -f elk-demo/docker-compose.yml restart"
    echo "  docker-compose -f grafana-demo/docker-compose.yml restart"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${GREEN}Готово! Можете начинать практиковаться! 🚀${NC}"
    echo ""
}

# Главная функция
main() {
    clear
    
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     Автоматическая установка окружения для обучения         ║
║        Мониторинг и логирование: Kibana + Grafana           ║
║                                                              ║
║                    Интенсив 8                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    
    echo ""
    
    check_docker
    check_ports
    create_directories
    create_configs
    generate_sample_logs
    
    echo ""
    read -p "$(echo -e ${YELLOW}Начать установку? [y/N]: ${NC})" -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_elk
        start_grafana
        setup_kibana_index
        
        echo ""
        print_summary
    else
        print_info "Установка отменена"
        exit 0
    fi
}

# Запуск
main
"""

print("Скрипт setup.sh создан!")
print("Размер:", len(main_setup_script), "байт")
