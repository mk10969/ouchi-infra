##### set env #####
set shell := ["bash", "-uc"]
set dotenv-load := true


##### variables ######
APP_VERSION := "v1.0.0"
REMOCON_RS_VERSION := "v0.3.3"
NODE_EXPORTER_VERSION := "1.1.2"
VMAGENT_VERSION := "v1.58.0"


##### commands ######
version:
    @echo {{ APP_VERSION }}

tag:
    git tag -a {{ APP_VERSION }} -m 'version up'

push:
    git push origin {{ APP_VERSION }}

update-remocon-rs:
   curl -sLf -H 'Accept: application/octet-stream' \
        -o ./roles/remocon-rs/files/remocon-rs-aarch64-unknown-linux-gnu \
        "https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/assets/$( \
            curl -sL https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/tags/{{ REMOCON_RS_VERSION }} \
            | jq '.assets[] | select(.name | contains("aarch64")) | .id')"

   curl -sLf -H 'Accept: application/octet-stream' \
        -o ./roles/remocon-rs/files/irrp.py \
        "https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/assets/$( \
            curl -sL https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/tags/{{ REMOCON_RS_VERSION }} \
            | jq '.assets[] | select(.name | contains("irrp.py")) | .id')"

   curl -sLf -H 'Accept: application/octet-stream' \
        -o ./roles/remocon-rs/files/codes.json \
        "https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/assets/$( \
            curl -sL https://$GITHUB_ACCESS_TOKEN@api.github.com/repos/mk10969/remocon-rs/releases/tags/{{ REMOCON_RS_VERSION }} \
            | jq '.assets[] | select(.name | contains("codes.json")) | .id')"

update-node-exporter:
    curl -sLf -o ./tmp/node_exporter-{{ NODE_EXPORTER_VERSION }}.linux-arm64.tar.gz \
        https://github.com/prometheus/node_exporter/releases/download/v{{ NODE_EXPORTER_VERSION }}/node_exporter-{{ NODE_EXPORTER_VERSION }}.linux-arm64.tar.gz
    tar zxf ./tmp/node_exporter-{{ NODE_EXPORTER_VERSION }}.linux-arm64.tar.gz -C ./tmp
    cp -pfr ./tmp/node_exporter-{{ NODE_EXPORTER_VERSION }}.linux-arm64/node_exporter ./roles/node-exporter/files/
    rm -fr ./tmp/node_exporter-{{ NODE_EXPORTER_VERSION }}.linux-arm64.tar.gz
    rm -fr ./tmp/node_exporter-{{ NODE_EXPORTER_VERSION }}.linux-arm64

update-vmagent:
    curl -sLf -o ./tmp/vmutils-arm64-{{ VMAGENT_VERSION }}.tar.gz \
        https://github.com/VictoriaMetrics/VictoriaMetrics/releases/download/{{ VMAGENT_VERSION }}/vmutils-arm64-{{ VMAGENT_VERSION }}.tar.gz
    mkdir -p ./tmp/vmutils
    tar zxf ./tmp/vmutils-arm64-{{ VMAGENT_VERSION }}.tar.gz -C ./tmp/vmutils
    cp -pfr ./tmp/vmutils/vmagent-prod ./roles/vmagent/files/vmagent
    rm -fr ./tmp/vmutils
    rm -fr ./tmp/vmutils-arm64-{{ VMAGENT_VERSION }}.tar.gz

