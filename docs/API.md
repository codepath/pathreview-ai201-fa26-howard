# API Reference

Base URL: `http://localhost:8000` · Interactive docs: [Swagger UI](http://localhost:8000/docs), [ReDoc](http://localhost:8000/redoc)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/` | — | Liveness check |
| GET | `/health` | — | Dependency health |
| POST | `/auth/register` | — | Create an account |
| POST | `/auth/login` | — | Get a JWT |
| POST | `/profiles` | Bearer | Create a profile |
| GET | `/profiles/{profile_id}` | Bearer | Get a profile |
| PUT | `/profiles/{profile_id}` | Bearer | Update a profile |
| DELETE | `/profiles/{profile_id}` | Bearer | Delete a profile and its reviews |
| POST | `/reviews` | Bearer | Request a review |
| GET | `/reviews/{review_id}` | Bearer | Get a review |
| GET | `/reviews/{review_id}/status` | Bearer | Get review progress |
| GET | `/reviews` | Bearer | List your reviews |

## Quick start

With the app running (`make run`), set these variables, then run the examples
below in order. Each one reuses the `TOKEN`, `PROFILE_ID`, or `REVIEW_ID` an
earlier one captured.

```bash
BASE_URL=http://localhost:8000
EMAIL=developer@example.com
PASSWORD='change-this-password'   # 8–128 characters
```

The capturing commands need [`jq`](https://jqlang.github.io/jq/). Without it,
drop the `| jq ...` part and copy the `access_token` or `id` from the output by
hand.

**Common errors:**
- `401`: `TOKEN` is missing or expired. Re-run the login example.
- `400` on register: the email already exists. Use login instead.
- `422`: the request body is invalid, for example a short password or a
  resume that isn't PDF, Markdown, or plain text.

## Status

`GET /` — Service name and version.

```bash
curl "$BASE_URL/"
```

`GET /health` — Returns `200` if PostgreSQL, Redis, and the vector store are
healthy, otherwise `503`.

```bash
curl "$BASE_URL/health"
```

> **Known issue:** `/health` currently returns `503` even when everything is
> running (#61, #62). Use `GET /` until those are fixed.

## Authentication

`POST /auth/register` — Create an account (JSON body) and return a token.

```bash
TOKEN=$(curl --silent --request POST "$BASE_URL/auth/register" \
  --header 'Content-Type: application/json' \
  --data "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
  | jq --raw-output '.access_token')
```

`POST /auth/login` — Get a token for an existing account. Takes form data, with
the email sent as `username`.

```bash
TOKEN=$(curl --silent --request POST "$BASE_URL/auth/login" \
  --data-urlencode "username=$EMAIL" \
  --data-urlencode "password=$PASSWORD" \
  | jq --raw-output '.access_token')
```

## Profiles

`POST /profiles` — Create a profile. Takes multipart form data; every field is
optional.

```bash
PROFILE_ID=$(curl --silent --request POST "$BASE_URL/profiles" \
  --header "Authorization: Bearer $TOKEN" \
  --form 'github_username=octocat' \
  --form 'portfolio_url=https://example.com' \
  | jq --raw-output '.id')
```

To attach a resume, add `--form 'resume_file=@resume.pdf'`. PDF, Markdown, and
plain-text files are accepted.

`GET /profiles/{profile_id}` — Get one of your profiles.

```bash
curl --header "Authorization: Bearer $TOKEN" "$BASE_URL/profiles/$PROFILE_ID"
```

`PUT /profiles/{profile_id}` — Update `github_username` and/or `portfolio_url`
(JSON body).

```bash
curl --request PUT "$BASE_URL/profiles/$PROFILE_ID" \
  --header "Authorization: Bearer $TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{"portfolio_url": "https://example.org"}'
```

## Reviews

`POST /reviews` — Request a review of a profile. Returns immediately with
`status: "pending"` while the review runs in the background.

```bash
REVIEW_ID=$(curl --silent --request POST "$BASE_URL/reviews" \
  --header "Authorization: Bearer $TOKEN" \
  --header 'Content-Type: application/json' \
  --data "{\"profile_id\": \"$PROFILE_ID\"}" \
  | jq --raw-output '.id')
```

`GET /reviews/{review_id}` — Get a review and its feedback sections.

```bash
curl --header "Authorization: Bearer $TOKEN" "$BASE_URL/reviews/$REVIEW_ID"
```

`GET /reviews/{review_id}/status` — Get a review's `status` and `progress_pct`.

```bash
curl --header "Authorization: Bearer $TOKEN" "$BASE_URL/reviews/$REVIEW_ID/status"
```

`GET /reviews` — List your reviews. `page` defaults to 1; `page_size` defaults
to 20 (max 100).

```bash
curl --header "Authorization: Bearer $TOKEN" "$BASE_URL/reviews?page=1&page_size=20"
```

## Clean up

`DELETE /profiles/{profile_id}` — Delete a profile **and its reviews**. Returns
`204`. Run this last; afterwards the IDs above return `404`.

```bash
curl --include --request DELETE "$BASE_URL/profiles/$PROFILE_ID" \
  --header "Authorization: Bearer $TOKEN"
```
