# Codex Cloud에서 Tailscale로 사내 서버에 접속하기

Codex Cloud는 작업마다 OpenAI 쪽에 새 VM을 띄웁니다. 원래 이 VM은 GitHub 저장소와 공개 인터넷까지만 닿습니다. 2026년 10월부터 환경 설정에서 VPN으로 **Tailscale**을 고를 수 있게 되어, 인터넷에 공개하지 않은 사내 API·테스트 서버에도 들어갈 수 있게 됐습니다.

이 문서는 영상에서 실제로 한 순서를 그대로 적은 것입니다. 상황은 이렇습니다.

- 사내 재고 API 서버가 v2로 바뀌었는데, 이 저장소의 `inventory/client.py`는 아직 옛 v1(`/v1/products`)에 맞춰져 있습니다.
- v2 응답 형식은 어디에도 문서로 남아 있지 않아서, 실제 서버를 봐야만 고칠 수 있습니다.
- 서버([codex-tailscale-demo-server](https://github.com/dante01yoon/codex-tailscale-demo-server))는 `:8080`(Codex에 열어 줄 API)과 `:9090`(막아야 할 관리자 포트)을 엽니다.

## 0. Tailscale 기초

- **tailnet**: 내 계정에 묶인 사설 네트워크입니다. 들어온 기기마다 `100.x.y.z` 주소가 붙습니다.
- **설치**: macOS·Windows·Linux·iOS(App Store)·Android(Google Play) 모두 지원합니다. Apple TV, Synology, Docker에도 설치할 수 있습니다. https://tailscale.com/download
- **요금**: 개인용 Personal 요금제는 무료이고, 사용자 6명까지 기기 수 제한 없이 씁니다. https://tailscale.com/pricing
- **이럴 때 씁니다**: 밖에서 휴대폰으로 집 NAS에 들어갈 때, 원격 개발 서버에 접속할 때, CI를 사내 자원에 연결할 때, subnet router로 Tailscale을 설치할 수 없는 기기를 연결할 때, 그리고 AI 에이전트를 사설망에 들일 때입니다.

## 1. 사내 API 서버를 tailnet에 올리기

이미 다른(예: 회사) tailnet에 들어가 있는 맥이라면, 맥은 그대로 두고 서버만 Docker 컨테이너로 개인 테스트 tailnet에 넣습니다.

```sh
git clone https://github.com/dante01yoon/codex-tailscale-demo-server
cd codex-tailscale-demo-server
./run.sh   # 처음 실행하면 로그인 링크가 출력됩니다
```

출력된 `https://login.tailscale.com/a/...` 링크를 열고 **Connect**를 누릅니다. 관리 콘솔 Machines에 `codex-demo-api`가 보이면 성공입니다. 이 기기의 `100.x` 주소를 적어 둡니다.

> `run.sh`의 `--advertise-tags=tag:demo-api`는 2단계 정책을 저장한 뒤에만 통과합니다. 처음에는 이 옵션을 빼고 로그인한 다음, 콘솔에서 태그를 붙여도 됩니다(3단계).

## 2. 접근 정책을 먼저 좁히기

새 tailnet의 기본 정책은 `{"src": ["*"], "dst": ["*"], "ip": ["*"]}`, 즉 "모든 기기가 모든 기기에 접근"입니다. 이대로 Codex를 연결하면 tailnet 전체가 Codex에게 열립니다.

관리 콘솔 → **Access controls → JSON editor**에서 [tailscale-policy.hujson](tailscale-policy.hujson)처럼 고칩니다.

```hujson
"tagOwners": {
  "tag:codex":    ["autogroup:admin"],
  "tag:demo-api": ["autogroup:admin"],
},
"grants": [
  {"src": ["autogroup:member"], "dst": ["*"], "ip": ["*"]},
  {"src": ["tag:codex"], "dst": ["tag:demo-api"], "ip": ["tcp:8080"]},
],
"tests": [
  {"src": "tag:codex", "accept": ["tag:demo-api:8080"], "deny": ["tag:demo-api:9090"]},
],
```

`tests`는 저장할 때마다 자동으로 돌아서, 규칙이 의도와 다르면 저장이 거부됩니다.

## 3. 서버에 태그 붙이기

Machines → `codex-demo-api` → ⋯ → **Edit ACL tags** → `tag:demo-api` → Save

## 4. Codex 전용 auth key 만들기

**Settings → Keys → Generate auth key…**

| 항목 | 값 | 이유 |
|---|---|---|
| Reusable | 켬 | 작업마다 새 VM이 같은 키로 들어옴 |
| Expiration | 짧게 (예: 7일) | 키가 새도 피해 기간이 짧음 |
| Ephemeral | 켬 | 꺼진 VM은 기기 목록에서 자동 삭제 |
| Tags | `tag:codex` | 키를 만든 사람의 권한이 아니라 태그 규칙을 따름 |

Reusable과 Ephemeral은 [OpenAI 문서](https://learn.chatgpt.com/docs/environments/cloud-environments)가 요구하는 설정이고, 태그는 [Tailscale 블로그](https://tailscale.com/blog/codex-cloud-tailscale)가 권하는 설정입니다. 키 값은 만들 때 한 번만 보입니다. 채팅창에는 붙여 넣지 마세요.

## 5. Codex Cloud 환경 만들기

1. ChatGPT의 Codex → **Cloud** → **Choose environment → Create environment**
2. 이 저장소를 고르고 **Get started**를 누릅니다. Codex가 저장소를 읽고 설치 스크립트를 스스로 준비합니다.
3. 사내 API 주소를 물으면 `http://100.x.y.z:8080`처럼 **Tailscale IP**로 답합니다. 이 주소는 비밀 정보가 아닙니다.
4. **Edit environment**에서 다음을 확인합니다.
   - Environment variables: `INTERNAL_API_URL`
   - Internet access → Additional allowed domains: 서버 IP(예: `100.85.0.14`). VPN 규칙과 이 허용 목록 **둘 다** 열려 있어야 합니다.
   - **Advanced → VPN → Tailscale ✏️**: 4단계 키를 붙여 넣고 저장합니다.
5. 환경을 **Publish**(또는 다시 게시)합니다.

## 6. 확인

새 작업에 이렇게 보냅니다.

> 사내 재고 API(INTERNAL_API_URL)가 v2로 바뀌었어. 실제 API 응답을 확인해서 inventory/client.py를 고치고, 실제 API로 test_live_report까지 통과시켜 줘.

영상에서 실제로 나온 결과입니다(2026-10-08).

| 환경 | 결과 |
|---|---|
| VPN 없음 | `100.85.0.14:8080/v2/items` HTTP 503, `vpn_configured: false` → 실제 응답을 못 봐서 코드를 고치지 않음 |
| Tailscale 연결 | 실제 `/v2/items` 응답을 확인하고 클라이언트 수정(+11 −2), 실제 API 테스트 포함 2개 통과, 1분 41초 |
| Tailscale 연결 + `:9090` 호출 | 연결 시간 초과(HTTP 503), 서버 기록에 9090 요청 0건 |

관리 콘솔 Machines에는 `codex-environment` 기기가 `tag:codex`, `Ephemeral` 표시를 달고 나타납니다.

## 지금의 제약 (2026-10 기준)

- HTTP·HTTPS 목적지만 바로 접속합니다. 그 밖의 TCP는 `proxy:8088`로 HTTP CONNECT를 거쳐야 합니다.
- SSH와 Tailscale SSH는 안 됩니다. Codex VM으로 들어오는 연결, UDP·ICMP도 안 됩니다.
- 주소는 IPv4를 씁니다. MagicDNS·split DNS는 Tailscale 블로그는 "안 된다", OpenAI 문서는 "된다"고 해서 서로 다릅니다. `100.x` 주소를 쓰면 확실합니다.
- 안전 수칙: 에이전트와 서버 양쪽에 태그를 붙이고, grants로 필요한 포트만 열고, 키에 만료를 걸고, 기기 승인(device approval)을 켭니다.

## 출처

- Tailscale, "Codex Cloud shipped with Tailscale support. Nobody told us." (2026-10-06) https://tailscale.com/blog/codex-cloud-tailscale
- OpenAI, Cloud environments — Private networking (VPN) https://learn.chatgpt.com/docs/environments/cloud-environments
- Tailscale 문서: What is Tailscale?, Auth keys, Tags, Grants, Ephemeral nodes, Device approval (tailscale.com/kb)
