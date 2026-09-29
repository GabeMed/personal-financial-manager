# Finance Manager: frontend

React 19 + TypeScript + Vite SPA for the Finance Manager API. See the
[root README](../../README.md) for the full picture.

```bash
npm ci
npm run dev      # http://localhost:5173
npm run lint
npm run build    # tsc -b && vite build
```

The API base URL comes from `VITE_API_URL` (default
`http://localhost:8000/api/v1`). The Docker image builds with `/api/v1` and
nginx proxies `/api` to the backend (see `Dockerfile` and `nginx.conf`).

| Folder | Contents |
| --- | --- |
| `src/context` | `AuthContext`: current user, login, logout |
| `src/hooks` | TanStack Query hooks, one per API operation |
| `src/services` | Axios client with the JWT interceptor, auth service, error helper |
| `src/schemas` | Zod schemas for the forms |
| `src/components` | Transactions list/form/dialogs, charts, Chakra UI snippets |
| `src/pages` | Login, registration, dashboard |
