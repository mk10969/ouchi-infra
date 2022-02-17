##### set env #####
set shell := ["bash", "-uc"]


##### variables ######
app_version                  := "v1.0.3"

# https://github.com/mk10969/ouchi-kubernetes
ouchi_k8s_version            := "v1.1.1"

# https://github.com/prometheus/node_exporter
node_exporter_version        := "1.3.1"


##### commands ######
# app version
version:
    @echo {{ app_version }}

# git tag
tag:
    git tag -a {{ app_version }} -m 'version up'

# tag push
push:
    git push origin {{ app_version }}

# argocd app update
argocd:
   curl -sLf -H 'Accept: application/octet-stream' \
        -o ./roles/k8s-argocd/files/argocd.yaml \
        "https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/ouchi-kubernetes/releases/assets/$( \
            curl -sL https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/ouchi-kubernetes/releases/tags/{{ ouchi_k8s_version }} \
            | jq '.assets[] | select(.name | contains("argocd.yaml")) | .id')"

# node-exporter update
node-exporter:
    @echo "For raspi4 model B"
    curl -sLf -o ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64.tar.gz \
        https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-arm64.tar.gz
    tar zxf ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64.tar.gz -C ./tmp
    cp -pfr ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64/node_exporter ./roles/node-exporter/files/node_exporter-arm64
    rm -fr ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64.tar.gz
    rm -fr ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64

    @echo "For raspi zero"
    curl -sLf -o ./tmp/node_exporter-{{ node_exporter_version }}.linux-armv6.tar.gz \
        https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-armv6.tar.gz
    tar zxf ./tmp/node_exporter-{{ node_exporter_version }}.linux-armv6.tar.gz -C ./tmp
    cp -pfr ./tmp/node_exporter-{{ node_exporter_version }}.linux-armv6/node_exporter ./roles/node-exporter/files/node_exporter-armv6
    rm -fr ./tmp/node_exporter-{{ node_exporter_version }}.linux-armv6.tar.gz
    rm -fr ./tmp/node_exporter-{{ node_exporter_version }}.linux-armv6
