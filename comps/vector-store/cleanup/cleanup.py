from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
import time

# Load Kubernetes config
try:
    config.load_incluster_config()
    print("Running inside Kubernetes cluster")
except ConfigException:
    config.load_kube_config()
    print("Running locally with kubeconfig")

apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

NAMESPACE = "vector-db"

def cleanup_expired_instances():
    """Delete deployments that have exceeded their TTL."""
    try:
        deployments = apps_v1.list_namespaced_deployment(
            namespace=NAMESPACE,
            label_selector="managed-by=vector-db-provisioner"
        )
        
        now = time.time()
        cleaned = 0
        
        for deployment in deployments.items:
            ttl_annotation = deployment.metadata.annotations.get("ttl")
            if ttl_annotation:
                ttl = int(ttl_annotation)
                if now > ttl:
                    username = deployment.metadata.labels.get("user")
                    print(f"Cleaning up expired instance for user: {username}")
                    
                    # Delete deployment
                    apps_v1.delete_namespaced_deployment(
                        name=deployment.metadata.name,
                        namespace=NAMESPACE,
                        body=client.V1DeleteOptions(
                            propagation_policy='Foreground'
                        )
                    )
                    
                    # Delete associated service
                    try:
                        core_v1.delete_namespaced_service(
                            name=f"qdrant-{username}",
                            namespace=NAMESPACE
                        )
                    except client.exceptions.ApiException as e:
                        if e.status != 404:
                            print(f"Error deleting service: {e}")
                    
                    cleaned += 1
                    print(f"Cleanup completed for user: {username}")
        
        print(f"Cleanup completed. Removed {cleaned} expired instances.")
    
    except Exception as e:
        print(f"Cleanup error: {e}")
        raise

if __name__ == "__main__":
    cleanup_expired_instances()
