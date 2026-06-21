# [OPEN] localstorage-ssr

## Bug Summary
- Frontend crashes on `GET /` with `ReferenceError: localStorage is not defined`.
- User also wants backend/frontend setup to be complete, authenticated, and easy to initialize.

## Hypotheses
1. `localStorage` is accessed during Nuxt server-side rendering in `frontend/app.vue` setup, before the browser environment exists.
2. Authentication state is initialized at module/setup evaluation time instead of client-only lifecycle time, causing SSR failure before the page renders.
3. There are additional browser-only globals used in the app bootstrap path that will fail after `localStorage` is fixed.
4. Frontend startup files are incomplete or inconsistent after cleanup, so SSR build output/runtime behavior differs from the intended auth flow.
5. Backend setup is missing a single bootstrap path, so even after frontend SSR is fixed, authentication and first-run setup will still be incomplete.

## Evidence Plan
- Reproduce the frontend SSR failure locally.
- Instrument the frontend bootstrap/auth initialization path with debug reporting.
- Verify whether SSR reaches the `localStorage` read before client mount.
- Check backend startup/setup flow and confirm what is missing for one-command initialization.

## Status
- Session created.
- Root cause confirmed from runtime stack trace and code path.
- Frontend SSR fix applied and verified by successful Nuxt production build.
- Backend bootstrap improved and schema compatibility fix added for older MySQL tables.

## Evidence
- `frontend/app.vue` previously read `localStorage` directly in `<script setup>`, which executes during Nuxt SSR.
- User-reported stack trace pointed to `frontend/app.vue` setup with `ReferenceError: localStorage is not defined`.
- Post-fix verification:
  - `npm run build` succeeds in `frontend/` with `NUXT_IGNORE_LOCK=1`.
  - `Invoke-WebRequest http://localhost:3000/` returns `200`.
  - `python bootstrap.py --skip-import --skip-seed --skip-train` succeeds in `backend/`.
  - `POST /api/auth/login` succeeds for the seeded admin user.

## Outcome
- Hypothesis 1 confirmed.
- Hypothesis 2 confirmed.
- Hypothesis 3 not observed after the SSR-safe auth/session update.
- Hypothesis 4 not primary cause.
- Hypothesis 5 confirmed and addressed with `backend/bootstrap.py` plus schema reconciliation.
