#!/bin/bash

source .env

# Debug print to confirm variables loaded
echo "NAMESPACE=$NAMESPACE"
echo "KAFKA_STREAMS_IMAGE=$KAFKA_STREAMS_IMAGE"
echo $(pwd)
# Add any other variable if needed...

./generate-values.sh

helm upgrade --install k8s-stream ../thulawa-helm-chart-deployment \
  --namespace "$NAMESPACE" \
  --create-namespace \
  -f ./values.generated.yaml
