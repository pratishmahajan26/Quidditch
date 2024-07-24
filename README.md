# Quidditch Setup on Local Machine
## Minikube:
- brew install minikube
- minikube start --cpus=6 --memory=8192
- minikube dashboard

## Helm:
- brew install helm

## Airflow:
- docker pull pratishmahajan26/airflow-trino:latest
- cd quidditch/helm-chart
- helm upgrade --install airflow ./airflow \
 	 --set images.airflow.repository=pratishmahajan26/airflow-trino \
 	 --set images.airflow.tag=latest \
  	 --set images.airflow.pullPolicy=Always
- kubectl get pods -o wide
- Visit http://127.0.0.1:8080 to use the application
- Default Webserver (Airflow UI) Login credentials:
     - username: admin
     - password: admin

## PostgreSQL:
- helm install my-postgres oci://registry-1.docker.io/bitnamicharts/postgresql 
- export POSTGRES_PASSWORD=$(kubectl get secret --namespace default my-postgres-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
- echo $POSTGRES_PASSWORD
- kubectl port-forward --namespace default svc/my-postgres-postgresql 5432:5432

## Trino
- cd quidditch/helm-chart
- helm install -f trino/custom-values.yml trino ./trino
- export POD_NAME=$(kubectl get pods --namespace default --selector "app.kubernetes.io/name=trino,app.kubernetes.io/instance=example-trino-cluster,app.kubernetes.io/component=coordinator" --output name)
- echo $POD_NAME
- kubectl port-forward $POD_NAME 8085:8085
- Visit http://127.0.0.1:8085 to use the application

## Presto
- cd quidditch/helm-chart
- helm install presto ./presto
- To access presto service within the cluster, use the following URL:
    - presto.default.svc.cluster.local
- To access presto service from outside the cluster for debugging, run the following command:
    - kubectl port-forward svc/presto 8090:8090 -n default
- Visit http://127.0.0.1:8090 to use the application

## Minio
- helm install minio --set resources.requests.memory=512Mi --set replicas=1 --set persistence.enabled=false --set mode=standalone --set rootUser=rootuser,rootPassword=rootpass123 minio/minio
- To access MinIO from localhost, run the below commands:
  - export POD_NAME=$(kubectl get pods --namespace default -l "release=minio-1721640558" -o jsonpath="{.items[0].metadata.name}")
  - kubectl port-forward $POD_NAME 9000:9001 --namespace default
  - Access MinIO server on http://localhost:9000

## Prometheus
- helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
- helm repo update
- helm install prometheus prometheus-community/prometheus
- export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=prometheus,app.kubernetes.io/instance=prometheus" -o jsonpath="{.items[0].metadata.name}")
- kubectl --namespace default port-forward $POD_NAME 9090
- Visit http://127.0.0.1:9090 to use the application


## Grafana
- helm repo add grafana https://grafana.github.io/helm-charts 
- helm repo update
- helm install grafana grafana/grafana
- Prometheus Server for Grafana: http://prometheus-server.default.svc.cluster.local
- Get your 'admin' user password by running:
  - kubectl get secret --namespace default grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
- export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=grafana" -o jsonpath="{.items[0].metadata.name}")
- kubectl --namespace default port-forward $POD_NAME 3000
- Visit http://127.0.0.1:3000 to use the application

## Get all helm releases
- helm list

## Uninstall
- helm uninstall RELEASE_NAME -n default