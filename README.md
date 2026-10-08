# Codex Cloud × Tailscale 실습

Codex Cloud 작업 VM을 내 tailnet에 넣어, 인터넷에 공개하지 않은 사내 API를 Codex가 직접 호출·테스트하게 만드는 실습입니다.

- 사내 API 서버는 이 저장소에 없습니다. [codex-tailscale-demo-server](https://github.com/dante01yoon/codex-tailscale-demo-server)에서 따로 돌리고, Codex는 tailnet으로만 닿습니다.
- `inventory/client.py` — **일부러 옛 v1 API에 맞춰 둔** 클라이언트. 사내 API가 v2로 바뀌었는데 응답 형식은 문서로 남아 있지 않아서, 실제 서버를 봐야 고칠 수 있습니다.
- `tailscale-policy.hujson` — Codex(`tag:codex`)가 데모 API의 8080만 쓰도록 막는 정책 예시

자세한 단계는 [TUTORIAL.md](TUTORIAL.md)를 보세요.
