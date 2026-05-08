# Fine-Tuned CLI Auth Plan Using Loopback Plus Exchange

## Summary
- Keep one Applika session model for both web and CLI:
  - `__access`: short-lived JWT
  - `__refresh`: opaque Redis-backed refresh token
- Do not add a separate CLI bearer-token model.
- Add a CLI login handoff so the CLI can receive those same session values safely after GitHub sign-in.

## Flow
1. `applika login` starts a temporary loopback server on a random localhost port.
2. The CLI generates a random `state`.
3. The CLI calls `POST /auth/cli/start` with `callback_url` and `state`.
4. The backend validates the callback target is loopback-only and stores a pending login in Redis.
5. The backend returns a `login_id` and `login_url`.
6. The CLI opens `login_url` in the browser.
7. The browser calls `GET /auth/cli/login/{login_id}`.
8. The backend sets a short-lived CLI login marker cookie and redirects into the normal GitHub OAuth flow.
9. GitHub redirects back to `GET /auth/github/callback`.
10. The backend runs the normal GitHub verification and user registration/update logic.
11. If there is no CLI marker cookie, the browser flow remains unchanged.
12. If the CLI marker cookie is present, the backend:
    - loads the pending CLI login from Redis
    - creates a single-use short-lived authorization code in Redis
    - clears the marker cookie
    - redirects the browser to the loopback callback with `code` and `state`
13. The CLI loopback server verifies `state`.
14. The CLI calls `POST /auth/cli/exchange` with the code.
15. The backend mints the real Applika session at exchange time:
    - generate `__access`
    - generate `__refresh`
16. The backend returns those values in JSON.
17. The CLI stores them in `~/.config/applika/session.json`.

## Backend Changes
- New endpoints:
  - `POST /auth/cli/start`
  - `GET /auth/cli/login/{login_id}`
  - `POST /auth/cli/exchange`
- Extend `GET /auth/github/callback` with the CLI handoff branch.
- Refactor token helpers so session values can be created independently from cookie writing.

## CLI Behavior
- Store:
  - `api_base_url`
  - `access_token`
  - `refresh_token`
  - `access_expires_at`
- Send `__access` and `__refresh` back as cookies on API calls.
- Reuse existing `GET /auth/refresh` and `GET /auth/logout`.
- Parse updated session cookies from refresh responses and persist them locally.

## Security
- Never put `__access` or `__refresh` in redirect URLs.
- Require exact `state` verification in the CLI callback.
- Use loopback-only callback URLs.
- Use short TTLs for pending logins and exchange codes.
- Make exchange codes single-use.
- Mint the real Applika session only at `/auth/cli/exchange`.
