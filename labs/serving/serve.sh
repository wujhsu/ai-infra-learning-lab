#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${MODEL:=Qwen/Qwen3-0.6B}"
: "${IMAGE:=vllm/vllm-openai:v0.29.0}"
if [[ -f experiment.env ]]; then source experiment.env; fi
: "${MODEL_REVISION:?Run python3 prepare.py first, or set a fixed model commit}"
docker pull "$IMAGE"
docker image inspect "$IMAGE" --format '{{json .RepoDigests}}' > image-digests.json
docker network inspect ai-infra-lab >/dev/null 2>&1 || docker network create ai-infra-lab
runtime_args=(--network ai-infra-lab)
model_args=("$MODEL" --revision "$MODEL_REVISION" --served-model-name lab-model --max-model-len 4096 --gpu-memory-utilization 0.8)
if [[ -n "${TRACE_ENDPOINT:-}" ]]; then
 runtime_args+=(-e OTEL_SERVICE_NAME=vllm-lab -e OTEL_EXPORTER_OTLP_TRACES_INSECURE=true)
 model_args+=(--otlp-traces-endpoint "$TRACE_ENDPOINT")
fi
docker run --rm --name inference-lab --gpus all -p 127.0.0.1:8000:8000 \
 "${runtime_args[@]}" --shm-size 2g -v "$PWD/model-cache:/root/.cache/huggingface" "$IMAGE" "${model_args[@]}"
