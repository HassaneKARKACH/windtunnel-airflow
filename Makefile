# Run from Ubuntu (WSL), at the repo root

CLUSTER    := windtunnel
NAMESPACE  := airflow
CHART_REPO := https://airflow.apache.org
CHART_VER  := 1.22.0

export KUBECONFIG := $(HOME)/.kube/windtunnel
export PATH       := $(HOME)/.local/bin:$(PATH)

# Built here from deploy/Dockerfile: keep the tag equal to defaultAirflowTag in deploy/values.yaml.
AIRFLOW_IMAGE := windtunnel-airflow:3.2.2

# Images the chart pulls with deploy/values.yaml: update them with the chart version.
PULLED_IMAGES := bitnamilegacy/postgresql:16.1.0-debian-11-r15 \
                 redis:7.2-bookworm \
                 quay.io/prometheus/statsd-exporter:v0.30.0

.PHONY: cluster image images chart down

# Without these labels the Airflow pods stay Pending.
cluster:
	kind create cluster --config deploy/kind-config.yaml --kubeconfig $(KUBECONFIG)
	kubectl label node $(CLUSTER)-worker workload=airflow-services
	kubectl label node $(CLUSTER)-worker2 workload=airflow-tasks

image:
	docker build -f deploy/Dockerfile -t $(AIRFLOW_IMAGE) .

# A new kind node starts empty: loading the images avoids a slow pull on every cluster.
# "kind load docker-image" fails with Docker's containerd image store on multi-platform
# images, so export a single platform to an archive and load that instead.
images: image
	for image in $(PULLED_IMAGES); do docker pull $$image; done
	docker save --platform linux/amd64 -o /tmp/$(CLUSTER)-images.tar $(AIRFLOW_IMAGE) $(PULLED_IMAGES)
	kind load image-archive --name $(CLUSTER) /tmp/$(CLUSTER)-images.tar
	rm /tmp/$(CLUSTER)-images.tar

chart:
	helm install airflow airflow --repo $(CHART_REPO) --version $(CHART_VER) \
		-n $(NAMESPACE) --create-namespace -f deploy/values.yaml

down:
	kind delete cluster --name $(CLUSTER) --kubeconfig $(KUBECONFIG)
