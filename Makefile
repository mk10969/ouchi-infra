# Makefile to update roles/xxxxx/files

NODE_EXPORTER_VERSION = 1.1.2

# .PHONY: all
# all:
# 	@echo Read docs/maintenance.md for the usage

.PHONY: update/node-exporter
update/node-exporter:
	curl -sLf -o ./tmp/node_exporter-$(NODE_EXPORTER_VERSION).linux-arm64.tar.gz \
		https://github.com/prometheus/node_exporter/releases/download/v$(NODE_EXPORTER_VERSION)/node_exporter-$(NODE_EXPORTER_VERSION).linux-arm64.tar.gz
	tar zxf ./tmp/node_exporter-$(NODE_EXPORTER_VERSION).linux-arm64.tar.gz -C ./tmp
	cp -pfr ./tmp/node_exporter-$(NODE_EXPORTER_VERSION).linux-arm64/node_exporter ./roles/node-exporter/files/
	rm -fr ./tmp/node_exporter-$(NODE_EXPORTER_VERSION).linux-arm64.tar.gz
	rm -fr ./tmp/node_exporter-$(NODE_EXPORTER_VERSION).linux-arm64
