# Portfolio_Backend

Standalone Python API for the portfolio frontend. It serves the portfolio
sections from SQLite and local media from `public/` and `src/Assets/`. External
image and video URLs stay in the seed data and are loaded directly by clients.

## Run locally

Requires Python 3.9 or newer; no third-party packages are needed.

```sh
python3 server/app.py
```

The database is created at `server/portfolio.sqlite3` and initialized from
`server/portfolio.json`. The API listens at `http://127.0.0.1:5000`.

## API routes

- `GET /api/health`
- `GET /api/portfolio`
- `GET /api/portfolio/{section}` where section is `profile`, `projects`,
  `certificates`, `education`, `experience`, or `skills`
- `GET /media/{path}` for local images and documents

## Deploy to Render

This repository includes a Render Blueprint in `render.yaml`. Create a new
Render Blueprint deployment from this repository. The web service binds to
Render's `PORT` and exposes `/api/health` as its health check.

The included free-tier service uses an ephemeral filesystem. The API only
exposes read endpoints, so its SQLite content is restored from the seed file
whenever it restarts. For persistent database edits, attach a persistent disk
and set `PORTFOLIO_DB_PATH` to a path on that disk.

## Connect the Vercel frontend

Add Vercel rewrites in the frontend repository's `vercel.json`, replacing the
destination host with the deployed Render service:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-SERVICE.onrender.com/api/:path*"
    },
    {
      "source": "/media/:path*",
      "destination": "https://YOUR-SERVICE.onrender.com/media/:path*"
    }
  ]
}
```

Then redeploy the Vercel frontend. These rewrites keep API and media requests on
the frontend's origin.

## Tests

```sh
python3 -m unittest discover -s server -p 'test_*.py'
```
