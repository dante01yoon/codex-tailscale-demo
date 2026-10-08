#!/bin/sh
# 맥을 회사 tailnet에 둔 채, 데모 서버만 개인 tailnet에 넣는다.
set -e
docker run -d --name codex-tailnet-demo --hostname codex-demo-api --entrypoint tailscaled \
  -v codex-tailnet-demo-state:/var/lib/tailscale tailscale/tailscale:latest \
  --tun=userspace-networking --statedir=/var/lib/tailscale
sleep 3
docker exec codex-tailnet-demo tailscale up --hostname=codex-demo-api --advertise-tags=tag:demo-api
docker run -d --name codex-demo-inventory --network container:codex-tailnet-demo \
  -v "$PWD/internal_api:/app:ro" python:3.12-alpine python /app/server.py
docker exec codex-tailnet-demo tailscale ip -4
