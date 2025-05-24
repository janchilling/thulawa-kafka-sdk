import time
import requests
import random
import logging
from kubernetes import client, config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Load Kubernetes config
try:
    config.load_incluster_config()
    logger.info("Loaded Kubernetes in-cluster config.")
except config.ConfigException:
    config.load_kube_config()
    logger.info("Loaded Kubernetes kubeconfig.")

NAMESPACE = "streamspace"
DEPLOYMENT_NAME = "kafka-streams-app"
# https://kubernetes.docker.internal:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
# PROMETHEUS_URL = "http://kafka-streams-service.streamspace.svc.cluster.local:8080/metrics"
PROMETHEUS_URL = "http://prometheus.streamspace.svc.cluster.local:9090/api/v1/query"

# Function to get metric values from Prometheus
def get_metric(metric_name):
    try:
        logger.info(f"Fetching metric: {metric_name}")
        response = requests.get(f"{PROMETHEUS_URL}?query={metric_name}")
        result = response.json().get("data", {}).get("result", [])
        if result:
            metric_value = float(result[0]["value"][1])
            logger.info(f"Received metric value for {metric_name}: {metric_value}")
            return metric_value
        else:
            logger.warning(f"No results found for {metric_name}.")
    except Exception as e:
        logger.error(f"Error fetching {metric_name}: {e}")
    return None

# Function to scale Kubernetes deployment
def scale_deployment(replicas):
    api = client.AppsV1Api()
    deployment = api.read_namespaced_deployment(name=DEPLOYMENT_NAME, namespace=NAMESPACE)
    deployment.spec.replicas = replicas
    api.patch_namespaced_deployment(name=DEPLOYMENT_NAME, namespace=NAMESPACE, body=deployment)
    logger.info(f"Scaled {DEPLOYMENT_NAME} to {replicas} replicas.")

# Fitness function to determine the best scaling decision
def evaluate_fitness(metrics):
    cpu_usage = metrics.get("thulawa_cpu_usage", 0)
    heap_used = metrics.get("thulawa_heap_memory_used", 0)
    heap_max = metrics.get("thulawa_heap_memory_max", 1)  # Avoid division by zero
    combined_throughput = metrics.get("thulawa-event-processing-rate", 0)

    heap_utilization = (heap_used / heap_max) * 100
    load_factor = (cpu_usage + heap_utilization) / 2  # Weighted Load Factor

    logger.info(f"CPU: {cpu_usage}% | Heap: {heap_utilization}% | Throughput: {combined_throughput}")

    # Fitness score logic (Higher score means more scaling required)
    fitness_score = load_factor + (combined_throughput * 0.1)  # Adjust throughput weight

    logger.info(f"Calculated fitness score: {fitness_score}")
    return fitness_score

# Genetic Algorithm-based Scaling
def ga_based_scaling():
    current_replicas = 1
    max_replicas = 5
    min_replicas = 1
    scaling_interval = 10  # Time between checks (seconds)
    prev_fitness_score = None

    while True:
        logger.info("Fetching metrics for scaling decision...")

        # Fetch all required metrics
        metrics = {
            "thulawa_cpu_usage": get_metric("thulawa_cpu_usage"),
            "thulawa_heap_memory_used": get_metric("thulawa_heap_memory_used"),
            "thulawa_heap_memory_max": get_metric("thulawa_heap_memory_max"),
            "thulawa_combined_throughput": get_metric("thulawa_combined_throughput"),
        }

        # If any metric is None, retry in the next cycle
        if any(value is None for value in metrics.values()):
            logger.warning("Metrics not fully available. Retrying...")
            time.sleep(scaling_interval)
            continue

        # Compute fitness score
        fitness_score = evaluate_fitness(metrics)

        # Compare with previous score to determine trend
        if prev_fitness_score is not None:
            trend = fitness_score - prev_fitness_score
            logger.info(f"Trend: {trend}")
        else:
            trend = 0  # No trend initially
            logger.info("Initial fitness score, no trend calculated.")

        prev_fitness_score = fitness_score

        # Scaling decision
        if fitness_score > 85 or trend > 10:  # Increase replicas
            new_replicas = min(current_replicas + random.randint(2, 4), max_replicas)
            logger.info(f"Scaling up to {new_replicas} replicas.")
        elif fitness_score < 30 and trend < -10:  # Decrease replicas
            new_replicas = max(current_replicas - random.randint(1, 2), min_replicas)
            logger.info(f"Scaling down to {new_replicas} replicas.")
        else:
            new_replicas = current_replicas  # Keep as is
            logger.info("No scaling needed, maintaining current replicas.")

        if new_replicas != current_replicas:
            scale_deployment(new_replicas)
            current_replicas = new_replicas

        time.sleep(scaling_interval)  # Adjust frequency dynamically if needed

if __name__ == "__main__":
    ga_based_scaling()
