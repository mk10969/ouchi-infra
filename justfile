##### set env #####
set shell := ["bash", "-uc"]


##### variables ######
app_version                  := "v1.0.0"

# https://github.com/mk10969/ouchi-kubernetes
ouchi_k8s_version            := "v1.1.1"

# https://github.com/prometheus/node_exporter
node_exporter_version        := "1.2.2"

# https://github.com/VictoriaMetrics/VictoriaMetrics
vmagent_version              := "v1.65.0"

REMOCON_RS_VERSION := "1"

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

# sensor-script update
sensor-script:
   curl -sLf -H 'Accept: application/octet-stream' \
        -o ./roles/sensor/files/irrp.py \
        "https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/assets/$( \
            curl -sL https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/tags/{{ REMOCON_RS_VERSION }} \
            | jq '.assets[] | select(.name | contains("irrp.py")) | .id')"

   curl -sLf -H 'Accept: application/octet-stream' \
        -o ./roles/sensor/files/codes.json \
        "https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/assets/$( \
            curl -sL https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/tags/{{ REMOCON_RS_VERSION }} \
            | jq '.assets[] | select(.name | contains("codes.json")) | .id')"

# node-exporter update
node-exporter:
    curl -sLf -o ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64.tar.gz \
        https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-arm64.tar.gz
    tar zxf ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64.tar.gz -C ./tmp
    cp -pfr ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64/node_exporter ./roles/node-exporter/files/
    rm -fr ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64.tar.gz
    rm -fr ./tmp/node_exporter-{{ node_exporter_version }}.linux-arm64

# vmagent update
vmagent:
    curl -sLf -o ./tmp/vmutils-arm64-{{ vmagent_version }}.tar.gz \
        https://github.com/VictoriaMetrics/VictoriaMetrics/releases/download/{{ vmagent_version }}/vmutils-arm64-{{ vmagent_version }}.tar.gz
    mkdir -p ./tmp/vmutils
    tar zxf ./tmp/vmutils-arm64-{{ vmagent_version }}.tar.gz -C ./tmp/vmutils
    cp -pfr ./tmp/vmutils/vmagent-prod ./roles/vmagent/files/vmagent
    rm -fr ./tmp/vmutils
    rm -fr ./tmp/vmutils-arm64-{{ vmagent_version }}.tar.gz

