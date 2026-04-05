# 🚀 Kafka E-commerce Streaming Pipeline

## 📌 Descripción del Proyecto

Este proyecto implementa un **pipeline de datos en tiempo real** basado en eventos para una plataforma e-commerce, utilizando Apache Kafka como sistema de mensajería distribuida y Snowflake como data warehouse analítico.

El sistema simula interacciones de usuarios (event-driven), las procesa en streaming, filtra datos inválidos y las persiste en Snowflake para su posterior análisis mediante dashboards.

Este enfoque replica una arquitectura moderna de datos basada en el patrón **Medallion Architecture (Bronze → Silver → Gold)**.

---

## 🎯 Objetivos

* Diseñar un pipeline end-to-end de datos en tiempo real
* Comprender el funcionamiento interno de Apache Kafka
* Implementar procesamiento streaming con control de offsets
* Integrar Kafka con Snowflake para analítica
* Construir una capa analítica lista para visualización

---

## 🧰 Stack Tecnológico

| Tecnología   | Uso                                      |
| ------------ | ---------------------------------------- |
| Docker       | Contenerización del entorno              |
| Apache Kafka | Ingesta y streaming de eventos           |
| Python       | Desarrollo de productores y consumidores |
| Snowflake    | Almacenamiento y modelado analítico      |

---

## 🏗️ Arquitectura

### 🔄 Flujo de Datos

```text
Producer (Python)
        ↓
Kafka Topic (raw_events_ecom)  →  BRONZE
        ↓
Stream Processor (Consumer + Producer)
        ↓
Kafka Topic (clean_events_ecom) → SILVER
        ↓
Snowflake Consumer
        ↓
Snowflake Tables & Views → GOLD
        ↓
Dashboard
```

---

## ⚙️ Configuración del Entorno

### 1. Levantar servicios con Docker

```bash
docker-compose up -d
```

Esto levanta:

* Kafka Broker + Controller
* Kafka UI (opcional para monitoreo)

---

### 2. Creación de Topics

```bash
./kafka-topics.sh --create --topic raw_events_ecom --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1

./kafka-topics.sh --create --topic clean_events_ecom --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1
```

### 📌 Configuración aplicada

* **Particiones:** 3 (permite paralelismo)
* **Replication factor:** 1 (entorno local con un solo broker)

---

## 🧪 Componentes del Pipeline

### 📤 Producer — `producer.py`

Simula eventos de usuarios en una plataforma e-commerce.

#### Características:

* Generación de eventos aleatorios
* Inclusión de datos inválidos para testing
* Uso de `customer_id` como key para particionamiento

#### Estructura del evento:

```json
{
  "event_id": "uuid",
  "customer_id": "int",
  "event_type": "view | add_to_cart | purchase",
  "amount": "float",
  "currency": "string",
  "event_timestamp": "datetime"
}
```

📌 **Importante:**
El uso de `customer_id` como clave garantiza que los eventos del mismo usuario se mantengan en la misma partición (ordering).

---

### 🔄 Stream Processor — `stream_processor.py`

Encargado del procesamiento en tiempo real.

#### Funcionalidad:

* Consume eventos desde `raw_events_ecom`
* Aplica validaciones:

  * Campos nulos
  * Montos negativos
* Produce eventos válidos a `clean_events_ecom`

#### Buenas prácticas implementadas:

* ❌ Auto-commit deshabilitado
* ✅ Commit manual post-procesamiento
* ✅ Garantía de no pérdida de datos

---

### 📥 Snowflake Consumer — `snowflake_consumer.py`

Carga los datos procesados en Snowflake.

#### Características:

* Consumo desde `clean_events_ecom`
* Uso de `snowflake.connector`
* Inserción eficiente con `write_pandas`

#### Optimización:

* Buffer de 10 eventos antes de insertar (micro-batching)

---

## ❄️ Modelo de Datos en Snowflake

### 🥈 Tabla (Silver Layer)

* `Kafka_events_ecom_silver`

Contiene eventos limpios y estructurados.

---

### 🥇 Capa Gold (Vistas Analíticas)

#### 📊 `daily_customer_revenue`

* Revenue total por cliente por día

#### 📊 `event_funnel`

* Conteo de eventos por tipo y fecha
* Permite analizar el funnel:

  * View → Add to Cart → Purchase

---

## 📈 Dashboard

> *(Agregar imagen aquí)*

El dashboard permite:

* 📊 Análisis de revenue por cliente
* 📅 Tendencias temporales
* 🔄 Funnel de conversión
* 📈 Actividad de usuarios

---

## 💡 Conceptos Clave Aplicados

Este proyecto permitió profundizar en:

* Arquitectura basada en eventos
* Kafka Topics, Partitions y Offsets
* Consumer Groups
* Control manual de commits
* Procesamiento en streaming
* Integración de sistemas OLTP → OLAP
* Patrón Medallion

---

## ⚠️ Limitaciones del Proyecto

* Single broker (sin alta disponibilidad)
* Validaciones básicas de datos
* No hay manejo de errores avanzado (DLQ)
* No se implementa schema registry

---

## 🚀 Mejoras Futuras

* Implementar **Schema Registry (Avro/Protobuf)**
* Agregar **Dead Letter Queue (DLQ)**
* Orquestación con **Apache Airflow**
* Procesamiento avanzado con **Spark Streaming o Flink**
* Escalamiento a múltiples brokers
* Implementar CI/CD

---

## 📚 Referencias

* YouTube: *Data with Jay*

---

## 👨‍💻 Autor

Proyecto desarrollado como parte del aprendizaje en **Data Engineering** enfocado en arquitecturas modernas de streaming.

---

## ⭐ Nota Final

Este proyecto representa una implementación base pero sólida de un pipeline en tiempo real, alineado con prácticas utilizadas en entornos productivos de datos.

---
