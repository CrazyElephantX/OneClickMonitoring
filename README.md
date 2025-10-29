# OneClickMonitoring

# Что включено
setup-monitoring.sh - Главный скрипт установки

Полностью автоматизирует процесс:

- Проверяет Docker и Docker Compose
- Проверяет доступность портов
- Создает всю структуру директорий
- Генерирует конфигурационные файлы
- Создает 40 записей демо-логов
- Запускает ELK и Grafana стеки
- Настраивает Kibana index pattern
- Красивый цветной вывод в терминале

# Как использовать

chmod +x setup-monitoring.sh

## Запустить
./setup-monitoring.sh

## Открыть браузер:
- Kibana: http://localhost:5601
- Grafana: http://localhost:3000 (admin/admin)

# Особенности
## Demo данные
- 20 Apache access logs с разными HTTP кодами (200, 404, 500, 403)
- 20 Application logs с уровнями INFO, WARN, ERROR, DEBUG
- Реалистичные IP адреса, User-Agents, timestamps

## Auto-configuration
- Kibana index pattern создается автоматически
- Grafana datasource уже подключен к Prometheus
- Node Exporter собирает метрики

# Что развернется

|Сервис|Порт|Назначение|
|-|--------|---|
|Kibana         |  5601  |  Анализ логов     |
|Grafana        |  3000  |  Дашборды метрик  |
|Elasticsearch  |  9200  |  Хранение логов   |
|Prometheus     |  9090  |  Сбор метрик      |
|Node Exporter  |  9100  |  Системные метрики|
|Logstash       |  6000  |  Обработка логов  |


# Окружение для практики: Kibana + Grafana

Автоматическая установка полного стека для обучения мониторингу и логированию.

## Что включено

### ELK Stack (Логирование)
- **Elasticsearch 8.13.0** - хранение и поиск логов
- **Logstash 8.13.0** - обработка и парсинг логов
- **Kibana 8.13.0** - визуализация и анализ логов
- **Sample данные** - 40 записей околореальных логов (Apache + Application)

### Grafana Stack (Мониторинг)
- **Prometheus** - сбор и хранение метрик
- **Node Exporter** - системные метрики (CPU, RAM, Disk, Network)
- **Grafana** - визуализация метрик и дашборды
- **Auto-provisioned datasource** - Prometheus уже подключен

## Требования

- **Docker** >= 20.10
- **Docker Compose** >= 1.29
- **Свободное место** >= 4 GB
- **Свободная RAM** >= 4 GB
- **Свободные порты**: 3000, 5601, 9090, 9100, 9200, 6000

## 🚀 Быстрый старт

### 1. Автоматическая установка (Рекомендуется)

```bash
# Сделать скрипт исполняемым
chmod +x setup.sh

# Запустить установку
./setup.sh
```

Скрипт автоматически:
- ✅ Проверит зависимости (Docker, Docker Compose)
- ✅ Проверит доступность портов
- ✅ Создаст все конфигурационные файлы
- ✅ Сгенерирует демонстрационные логи
- ✅ Запустит все сервисы
- ✅ Настроит Kibana index pattern

**Время установки:** 3-5 минут (зависит от скорости интернета)

### 2. Ручная установка

Если автоматический скрипт не работает:

```bash
# ELK Stack
cd elk-demo
docker-compose up -d
cd ..

# Grafana Stack
cd grafana-demo
docker-compose up -d
cd ..
```

## Доступ к сервисам

После успешной установки:

| Сервис | URL | Авторизация |
|--------|-----|-------------|
| **Kibana** | http://localhost:5601 | Не требуется |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | Не требуется |
| **Elasticsearch** | http://localhost:9200 | Не требуется |
| **Node Exporter** | http://localhost:9100/metrics | Не требуется |

## Быстрые примеры

### Kibana

1. Откройте http://localhost:5601
2. Перейдите в **Discover**
3. Попробуйте поиски:
   ```
   response:404
   response >= 500
   request:POST AND response >= 400
   ```

### Grafana

1. Откройте http://localhost:3000
2. Войдите (admin/admin)
3. Перейдите в **Explore**
4. Попробуйте запросы:
   ```promql
   # CPU usage
   100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
   
   # Memory usage
   (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
   ```

## Управление

### Проверка статуса

```bash
chmod +x status.sh
./status.sh
```

### Остановка сервисов

```bash
chmod +x stop.sh
./stop.sh
```

Или вручную:
```bash
docker-compose -f elk-demo/docker-compose.yml down
docker-compose -f grafana-demo/docker-compose.yml down
```

### Перезапуск

```bash
# ELK
docker-compose -f elk-demo/docker-compose.yml restart

# Grafana
docker-compose -f grafana-demo/docker-compose.yml restart
```

### Просмотр логов

```bash
# Логи Elasticsearch
docker logs monitoring-elasticsearch

# Логи Kibana
docker logs monitoring-kibana

# Логи Grafana
docker logs monitoring-grafana

# Логи Prometheus
docker logs monitoring-prometheus

# Все логи ELK
docker-compose -f elk-demo/docker-compose.yml logs -f

# Все логи Grafana stack
docker-compose -f grafana-demo/docker-compose.yml logs -f
```

### Генерация дополнительных логов

```bash
chmod +x generate-more-logs.sh
./generate-more-logs.sh
```

Затем перезапустите Logstash:
```bash
docker restart monitoring-logstash
```

### Полное удаление

```bash
chmod +x cleanup.sh
./cleanup.sh
```

Или вручную:
```bash
# Удалить контейнеры и volumes
docker-compose -f elk-demo/docker-compose.yml down -v
docker-compose -f grafana-demo/docker-compose.yml down -v

# Удалить директории
rm -rf elk-demo grafana-demo
```

## Troubleshooting

### Порты заняты

Если порты заняты, найдите процесс:
```bash
# macOS/Linux
lsof -i :5601
lsof -i :3000

# Остановить конфликтующий сервис
sudo systemctl stop kibana
sudo systemctl stop grafana-server
```

### Elasticsearch не запускается

Увеличьте vm.max_map_count:
```bash
# Временно (до перезагрузки)
sudo sysctl -w vm.max_map_count=262144

# Постоянно
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### Мало памяти

Уменьшите выделенную память в docker-compose.yml:
```yaml
environment:
  - "ES_JAVA_OPTS=-Xms256m -Xmx256m"  # вместо 512m
```

### Нет данных в Kibana

1. Проверьте индексы в Elasticsearch:
```bash
curl http://localhost:9200/_cat/indices?v
```

2. Проверьте логи Logstash:
```bash
docker logs monitoring-logstash
```

3. Пересоздайте index pattern в Kibana:
   - Stack Management → Index Patterns → Create → `sample-logs-*`

### Grafana не показывает метрики

1. Проверьте Prometheus targets:
   http://localhost:9090/targets

2. Проверьте подключение в Grafana:
   - Configuration → Data Sources → Prometheus → Test

3. Проверьте Node Exporter:
```bash
curl http://localhost:9100/metrics
```

## Структура проекта

```
.
├── setup-monitoring.sh                      # Автоматическая установка
├── stop_script.sh                           # Остановка всех сервисов
├── cleanup_script.sh                        # Полное удаление
├── status_script.sh                         # Проверка статуса
├── generate-more-logs_script.sh             # Генератор логов
├── README.md                                # Эта документация
│
├── elk-demo/
│   ├── docker-compose.yml            # ELK stack
│   ├── logstash-pipeline/
│   │   └── logstash.conf             # Pipeline конфигурация
│   └── sample-logs/
│       ├── apache-access.log         # Sample Apache логи
│       └── application.log           # Sample application логи
│
└── grafana-demo/
    ├── docker-compose.yml            # Grafana stack
    ├── prometheus/
    │   └── prometheus.yml            # Prometheus конфигурация
    └── grafana/
        └── provisioning/
            ├── datasources/
            │   └── prometheus.yml    # Auto datasource
            └── dashboards/
                └── dashboards.yml    # Dashboard provider
```

## Практические задания

### Задание 1: Kibana
1. Найти все серверные ошибки (5xx)
2. Создать Pie chart распределения HTTP кодов
3. Создать дашборд с 3 визуализациями

### Задание 2: Grafana
1. Создать панель CPU Usage (Time series)
2. Создать панель Memory Usage (Stat)
3. Создать дашборд "Server Health"
4. Настроить алерт на CPU > 80%

### Задание 3: Интеграция
1. Добавить в логи correlation ID
2. Связать метрики с логами по времени
3. Создать единый view инцидента

## Полезные ссылки

### Документация
- [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Kibana](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Logstash](https://www.elastic.co/guide/en/logstash/current/index.html)
- [Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Grafana](https://grafana.com/docs/grafana/latest/)

### Готовые дашборды
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [Node Exporter Full](https://grafana.com/grafana/dashboards/1860)

### Обучающие материалы
- [Kibana Query Language (KQL)](https://www.elastic.co/guide/en/kibana/current/kuery-query.html)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)

## FAQ

**Q: Можно ли использовать в production?**
A: Нет, это демо-окружение. Для production нужно настроить security, backup, high availability.

**Q: Сколько места займет?**
A: ~3-4 GB (Docker images + volumes).

**Q: Как долго хранятся данные?**
A: Elasticsearch - 7 дней, Prometheus - 200 часов. Настраивается в конфигах.

**Q: Можно ли изменить порты?**
A: Да, отредактируйте docker-compose.yml файлы.

**Q: Есть ли данные после перезапуска?**
A: Да, данные хранятся в Docker volumes и сохраняются.

**Q: Как обновить до новых версий?**
A: Измените версии в docker-compose.yml и выполните `docker-compose up -d --build`.

## Советы

1. **Performance**: Если медленно, уменьшите выделенную память в docker-compose
2. **Логи**: Включайте DEBUG уровень только для отладки
3. **Алерты**: Не создавайте слишком много - alert fatigue реален
4. **Дашборды**: Используйте готовые из библиотеки как шаблоны
5. **Backup**: Экспортируйте дашборды (Saved Objects в Kibana, Export в Grafana)

## Поддержка

При проблемах:
1. Проверьте логи контейнеров
2. Проверьте статус через status_script.sh
3. Посмотрите раздел Troubleshooting
4. Задайте вопрос в чате курса

## Changelog

### v1.0.0 (2025-10-29)
- Первая версия
- ELK Stack 8.13.0
- Grafana OSS latest
- Prometheus latest
- Автоматическая установка