# proto/Makefile
PROTOC_VERSION ?= 3.21.12
PROTOC_GEN_GO_VERSION ?= 1.28.1
PROTOC_GEN_GO_GRPC_VERSION ?= 1.2.0

GO_PATH = ../golang/models/genproto
PY_PATH = ../python/models/genproto

.PHONY: proto-golang
proto-golang:
	@echo "Generating Golang protobuf files to $(GO_PATH)..."
	@mkdir -p $(GO_PATH)
	@protoc \
		--go_out=$(GO_PATH) \
		--go_opt=paths=source_relative \
		--go-grpc_out=$(GO_PATH) \
		--go-grpc_opt=paths=source_relative \
		--proto_path=. \
		filter_sync.proto

.PHONY: proto-python
proto-python:
	@echo "Generating Python protobuf files to $(PY_PATH)..."
	@mkdir -p $(PY_PATH)
	python -m grpc_tools.protoc \
		--proto_path=. \
		--python_out=$(PY_PATH) \
		--grpc_python_out=$(PY_PATH) \
		filter_sync.proto

.PHONY: proto-all
proto-all: proto-golang proto-python
	@echo "All protobuf files generated"

.PHONY: clean
clean:
	rm -rf $(GO_PATH)/*
	rm -rf $(PY_PATH)/*