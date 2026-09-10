# Cloudflare deployment contract

Cloudflare resources are intentionally not duplicated in this repository. Infrastructure source of truth:

```text
/home/cvsz/zworkforce/infrastructure/terraform/cloudflare
```

Expected route:

```text
zcoin.zeaz.dev -> existing ZeaZDev Cloudflare Tunnel -> http://127.0.0.1:18082
```

Expected controls:

- proxied CNAME to the existing tunnel
- Cloudflare Access self-hosted application with exact operator-email allowlist
- tunnel ingress entry before the terminal `http_status:404` rule
- `manage_tunnel_config` stays guarded until the complete live ingress is represented and reviewed

Do not reuse `18080`; it is reserved by zDash. Do not point the tunnel directly to FastAPI port 8000.

Deploy local origin first:

```bash
cd ~/zcoin
./deploy/deploy.sh
curl http://127.0.0.1:18082/backend-healthz
```

Then apply the reviewed Cloudflare plan from `zworkforce` and verify `https://zcoin.zeaz.dev/`.
