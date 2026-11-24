# Chronopoli clickable demo

58 Chronopoli windows filled with illustrative demo data, linked so you can click
through them like the real product: top menu, account menu, buttons, cards, a
guided navigator (← / → keys, M for the site map) and an offline AI Tutor.

Illustrative demo data only. Not a live platform. Tether is shown as an
illustrative demo partner; no partnership is implied.

## Run with Docker

```bash
cd demo
docker compose up -d --build
```

Then open <http://localhost:8080>. Stop it with `docker compose down`.

## Run without Docker

Open `demo/site/index.html` in Chrome or Safari. Everything works offline.
