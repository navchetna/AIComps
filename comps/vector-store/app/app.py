from fastapi import FastAPI, HTTPException
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from kubernetes.client.rest import ApiException
import time
import os
from dotenv import load_dotenv
from typing import Dict, Any
from datetime import datetime

app = FastAPI()
load_dotenv()

def load_k8s_config():
    try:
        config.load_incluster_config()
        print("Loaded in-cluster Kubernetes config")
    except ConfigException:
        try:
            config.load_kube_config()
            print("Loaded local kubeconfig")
        except ConfigException as e:
            print(f"Could not load Kubernetes config: {e}")
            raise

load_k8s_config()

# Initialize K8s API clients
apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()


NAMESPACE = "vector-db"
DEFAULT_TTL = 1800
QDRANT_IMAGE = "qdrant/qdrant:latest"
NODE_PORT_RANGE_START = 30000
NODE_PORT_RANGE_END = 32767

# In-memory tracking
instances: Dict[str, Dict[str, Any]] = {}


def create_qdrant_deployment(username: str) -> str:
    """Create a Kubernetes Deployment for Qdrant."""
    deployment_name = f"qdrant-{username}"
    
    # Define the host path for this user's data
    user_data_path = f"/mnt/qdrant-data/{username}"
    
    # Define deployment manifest
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(
            name=deployment_name,
            labels={
                "app": "qdrant",
                "user": username,
                "managed-by": "vector-db-provisioner"
            },
            annotations={
                "ttl": str(int(time.time()) + DEFAULT_TTL),
                "created-at": datetime.utcnow().isoformat()
            }
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": "qdrant", "user": username}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": "qdrant", "user": username}
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="qdrant",
                            image=QDRANT_IMAGE,
                            ports=[client.V1ContainerPort(container_port=6333)],
                            resources=client.V1ResourceRequirements(
                                requests={"memory": "512Mi", "cpu": "250m"},
                                limits={"memory": "1Gi", "cpu": "500m"}
                            ),
                            # Mount persistent storage for user data
                            volume_mounts=[
                                client.V1VolumeMount(
                                    name="qdrant-storage",
                                    mount_path="/qdrant/storage"
                                )
                            ]
                        )
                    ],
                    volumes=[
                        client.V1Volume(
                            name="qdrant-storage",
                            host_path=client.V1HostPathVolumeSource(
                                path=user_data_path,
                                type="DirectoryOrCreate"  # Creates directory if it doesn't exist
                            )
                        )
                    ]
                )
            )
        )
    )
    
    try:
        apps_v1.create_namespaced_deployment(
            namespace=NAMESPACE,
            body=deployment
        )
        return deployment_name
    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Failed to create deployment: {e}")


def create_qdrant_service(username: str, node_port: int = None) -> Dict[str, Any]:
    """Create a Kubernetes Service to expose Qdrant."""
    service_name = f"qdrant-{username}"
    
    # Define service manifest
    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name=service_name,
            labels={
                "app": "qdrant",
                "user": username,
                "managed-by": "vector-db-provisioner"
            }
        ),
        spec=client.V1ServiceSpec(
            type="NodePort",
            selector={"app": "qdrant", "user": username},
            ports=[
                client.V1ServicePort(
                    port=6333,
                    target_port=6333,
                    node_port=node_port
                )
            ]
        )
    )
    
    try:
        svc = core_v1.create_namespaced_service(
            namespace=NAMESPACE,
            body=service
        )
        # Get the assigned NodePort
        assigned_port = svc.spec.ports[0].node_port
        return {"service_name": service_name, "port": assigned_port}
    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Failed to create service: {e}")


def get_node_external_ip() -> str:
    """Get the external IP of a node in the cluster."""
    node_ip = os.getenv("NODE_IP")
    if node_ip:
        return node_ip

    return "localhost"


def wait_for_deployment_ready(deployment_name: str, timeout: int = 60):
    """Wait for deployment to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            deployment = apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=NAMESPACE
            )
            if deployment.status.ready_replicas == deployment.spec.replicas:
                return True
        except ApiException:
            pass
        time.sleep(2)
    return False


@app.post("/create_instance")
def create_instance(user: str):
    """Create a Qdrant instance for a user."""

    if not user.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid username format")
    
    username = user.lower()
    now = time.time()
    
    # Check if instance already exists
    if username in instances:
        info = instances[username]
        remaining = max(0, int(info["expiry"] - now))
        
        if remaining > 0:
            return {
                "message": f"Instance already exists for {username}",
                "user": username,
                "ip": info["ip"],
                "port": info["port"],
                "ttl": remaining,
                "status": "active"
            }
    
    try:
        # Create deployment
        deployment_name = create_qdrant_deployment(username)
        
        # Create service
        service_info = create_qdrant_service(username)
        
        # Wait for deployment to be ready
        if not wait_for_deployment_ready(deployment_name):
            raise HTTPException(
                status_code=500,
                detail="Deployment creation timeout"
            )
        
        # Get node IP
        node_ip = get_node_external_ip()
        
        # Store instance info
        expiry = now + DEFAULT_TTL
        instances[username] = {
            "deployment": deployment_name,
            "service": service_info["service_name"],
            "port": service_info["port"],
            "ip": node_ip,
            "expiry": expiry,
            "created_at": now
        }
        
        return {
            "user": username,
            "ip": node_ip,
            "port": service_info["port"],
            "ttl": DEFAULT_TTL,
            "status": "created",
            "connection_string": f"http://{node_ip}:{service_info['port']}"
        }
        
    except Exception as e:
        # Cleanup on failure
        cleanup_user_resources(username)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete_instance/{user}")
def delete_instance(user: str):
    """Manually delete a user's Qdrant instance."""
    username = user.lower()
    
    if username not in instances:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    cleanup_user_resources(username)
    del instances[username]
    
    return {"message": f"Instance for {username} deleted", "status": "deleted"}


@app.get("/instance_status/{user}")
def instance_status(user: str):
    """Check status of a user's instance."""
    username = user.lower()
    
    if username not in instances:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    info = instances[username]
    now = time.time()
    remaining = max(0, int(info["expiry"] - now))
    
    return {
        "user": username,
        "ip": info["ip"],
        "port": info["port"],
        "ttl": remaining,
        "status": "active" if remaining > 0 else "expired"
    }


def cleanup_user_resources(username: str):
    """Delete all Kubernetes resources for a user."""
    deployment_name = f"qdrant-{username}"
    service_name = f"qdrant-{username}"
    
    try:
        # Delete deployment
        apps_v1.delete_namespaced_deployment(
            name=deployment_name,
            namespace=NAMESPACE,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground'
            )
        )
    except ApiException as e:
        if e.status != 404:
            print(f"Error deleting deployment: {e}")
    
    try:
        # Delete service
        core_v1.delete_namespaced_service(
            name=service_name,
            namespace=NAMESPACE
        )
    except ApiException as e:
        if e.status != 404:
            print(f"Error deleting service: {e}")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Ensure namespace exists on startup."""
    try:
        core_v1.read_namespace(name=NAMESPACE)
    except ApiException as e:
        if e.status == 404:
            # Create namespace
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=NAMESPACE)
            )
            core_v1.create_namespace(body=namespace)
