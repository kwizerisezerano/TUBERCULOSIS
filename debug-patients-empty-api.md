# [OPEN] patients-empty-api

## Bug Summary
- Frontend appears not to show patients or diagnoses even though backend/database may already have records.
- User suspects frontend is not using backend API correctly.

## Hypotheses
1. JWT token is missing, expired, or not attached, so protected backend endpoints return unauthorized responses and the UI shows empty arrays.
2. Frontend API base URL or route usage is incorrect, so requests are not reaching the Flask backend.
3. Backend response shape differs from what the frontend expects for patients or diagnoses.
4. Diagnosis/patient save flow is not committing records correctly in the backend.
5. Frontend state or search filtering is hiding valid records after successful API responses.

## Evidence Plan
- Inspect frontend API calls and backend endpoint contracts.
- Add instrumentation to the frontend request/response path first.
- Reproduce the issue against the running app/backend.
- Confirm which hypothesis is supported by runtime evidence before applying a fix.

## Status
- Session created.
- Runtime evidence collected from frontend and backend.
- Backend JWT fix applied in code.
- Frontend error handling improved so failed API calls no longer appear as empty results.

## Evidence
- Live backend health endpoint reports `22167` patients and `5` users.
- Frontend debug logs show:
  - `/auth/me` request sent with token
  - `/patients?search=` request sent with token
  - `/alerts` request sent with token
  - all three responses returned `422`
  - frontend then set patient count to `0`
- Direct HTTP call to protected endpoint returned `{"msg":"Subject must be a string"}`.

## Root Cause
- Login created JWT tokens with a dictionary identity instead of a string subject.
- Protected endpoints rejected those tokens, so the frontend received failed responses and showed empty state.
- The frontend also treated non-OK responses like empty data instead of surfacing an error.

## Outcome
- Backend now creates JWT access tokens with string identity and keeps username/role in additional claims.
- Backend protected routes now read the user from string JWT identity.
- Frontend now throws on non-OK API responses instead of silently showing empty arrays.
- Frontend Patients view now displays backend total counts and paginates through results instead of implying only the first 20 records exist.

## Additional Evidence
- Live backend `/api/health` returned `patients: 22167`, then later `22168` after new activity.
- Live frontend/browser logs now show:
  - `/auth/me` -> `200`
  - `/patients?page=1&per_page=20&search=` -> `200`
  - `count: 20`
  - `total: 22168`
  - `pages: 1109`
- This confirms the frontend is using real backend data, but was previously missing pagination context.
