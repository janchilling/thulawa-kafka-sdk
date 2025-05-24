#!/bin/bash

source .env

# List of required environment variables
REQUIRED_VARS=(
  NAMESPACE
  KAFKA_STREAMS_IMAGE
  KAFKA_STREAMS_REPLICAS
  KAFKA_STREAMS_CPU_REQUEST
  KAFKA_STREAMS_MEMORY_REQUEST
  KAFKA_STREAMS_CPU_LIMIT
  KAFKA_STREAMS_MEMORY_LIMIT
  KAFKA_AUTOSCALER_IMAGE
  KAFKA_AUTOSCALER_CPU_REQUEST
  KAFKA_AUTOSCALER_MEMORY_REQUEST
  KAFKA_AUTOSCALER_CPU_LIMIT
  KAFKA_AUTOSCALER_MEMORY_LIMIT
  PROMETHEUS_IMAGE
  PROMETHEUS_CPU_REQUEST
  PROMETHEUS_MEMORY_REQUEST
  PROMETHEUS_CPU_LIMIT
  PROMETHEUS_MEMORY_LIMIT
  HPA_MIN_REPLICAS
  HPA_MAX_REPLICAS
  HPA_CPU_UTILIZATION
  INGRESS_ENABLED
  SERVICE_TYPE
  SERVICE_PORT
)

# Check all variables are set and non-empty
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var}" ]]; then
    echo "Environment variable '$var' is not set or empty."
    exit 1
  fi
done

# Optional: set defaults (uncomment if you want fallback values)
# KAFKA_STREAMS_CPU_LIMIT="${KAFKA_STREAMS_CPU_LIMIT:-500m}"
# KAFKA_STREAMS_MEMORY_LIMIT="${KAFKA_STREAMS_MEMORY_LIMIT:-256Mi}"

# Generate the values file
cat <<EOF > values.generated.yaml
namespace: ${NAMESPACE}

kafkaStreamsApp:
  image: ${KAFKA_STREAMS_IMAGE}
  replicas: ${KAFKA_STREAMS_REPLICAS}
  resources:
    requests:
      cpu: "${KAFKA_STREAMS_CPU_REQUEST}"
      memory: "${KAFKA_STREAMS_MEMORY_REQUEST}"
    limits:
      cpu: "${KAFKA_STREAMS_CPU_LIMIT}"
      memory: "${KAFKA_STREAMS_MEMORY_LIMIT}"

kafkaAutoscaler:
  image: ${KAFKA_AUTOSCALER_IMAGE}
  resources:
    requests:
      cpu: "${KAFKA_AUTOSCALER_CPU_REQUEST}"
      memory: "${KAFKA_AUTOSCALER_MEMORY_REQUEST}"
    limits:
      cpu: "${KAFKA_AUTOSCALER_CPU_LIMIT}"
      memory: "${KAFKA_AUTOSCALER_MEMORY_LIMIT}"

prometheus:
  image: ${PROMETHEUS_IMAGE}
  resources:
    requests:
      cpu: "${PROMETHEUS_CPU_REQUEST}"
      memory: "${PROMETHEUS_MEMORY_REQUEST}"
    limits:
      cpu: "${PROMETHEUS_CPU_LIMIT}"
      memory: "${PROMETHEUS_MEMORY_LIMIT}"

hpa:
  minReplicas: ${HPA_MIN_REPLICAS}
  maxReplicas: ${HPA_MAX_REPLICAS}
  cpuUtilization: ${HPA_CPU_UTILIZATION}

ingress:
  enabled: ${INGRESS_ENABLED}

service:
  type: ${SERVICE_TYPE}
  port: ${SERVICE_PORT}
EOF

echo "values.generated.yaml has been created successfully."
echo $(pwd)
echo ${PROMETHEUS_CPU_LIMIT}
