# Makefile to update roles/xxxxx/files

NODE_EXPORTER_VERSION = 1.1.2
VMAGENT_VERSION = v1.58.0

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

update/vmagent:
	curl -sLf -o ./tmp/vmutils-arm64-$(VMAGENT_VERSION).tar.gz \
		https://github.com/VictoriaMetrics/VictoriaMetrics/releases/download/$(VMAGENT_VERSION)/vmutils-arm64-$(VMAGENT_VERSION).tar.gz
	mkdir -p ./tmp/vmutils
	tar zxf ./tmp/vmutils-arm64-$(VMAGENT_VERSION).tar.gz -C ./tmp/vmutils
	cp -pfr ./tmp/vmutils/vmagent-prod ./roles/vmagent/files/vmagent
	rm -fr ./tmp/vmutils
	rm -fr ./tmp/vmutils-arm64-$(VMAGENT_VERSION).tar.gz
