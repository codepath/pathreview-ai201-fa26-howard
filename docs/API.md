# API Reference

Base URL: `http://localhost:8000`

Start the application before running these examples:

```bash
make run
```

The examples are meant to be run top to bottom in one terminal. They use these
shell variables, and later commands reuse the `TOKEN`, `PROFILE_ID`, and
`REVIEW_ID` values that earlier commands capture:

```bash
BASE_URL=http://localhost:8000
EMAIL=developer@example.com
PASSWORD='change-this-password'
```

The capturing commands pipe the JSON response through
[`jq`](https://jqlang.github.io/jq/) (`brew install jq` on macOS,
`sudo apt-get install jq` on Debian/Ubuntu, `winget install jqlang.jq` on
Windows). Without `jq`, drop the `| jq ...` part, run the `curl` command, and
copy the `access_token` or `id` value from the output into the variable by
hand, for example `TOKEN=eyJhbGciOi...`.

Protected endpoints return `401` when `TOKEN` is missing or expired; run the
login example again to get a fresh token.

## Endpoints

### Root

`GET /` — Returns a short service message and the API version.

```bash
curl "$BASE_URL/"
```

### Health

`GET /health` — Returns service status and dependency health. It responds
`200` when PostgreSQL, Redis, and the vector store are all healthy and `503`
otherwise.

```bash
curl "$BASE_URL/health"
```

> **Known issue:** on the current codebase this endpoint reports `postgres`
> and `redis` as `unhealthy` and returns `503` even when both services are
> running (see #61 and #62). Until those are fixed, use `GET /` to check that
> the API is up.

### Authentication

#### Register

`POST /auth/register` — Create a new account and return a JWT access token.

```bash
TOKEN=$(curl --silent --request POST "$BASE_URL/auth/register" \
  --header 'Content-Type: application/json' \
  --data "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
  | jq --raw-output '.access_token')
```

The password must be 8–128 characters (otherwise `422`). Registering an email
that already exists returns `400 Email already registered`; use the login
example below instead, or change `EMAIL`.

#### Login

`POST /auth/login` — Obtain a JWT access token for an existing account. This
endpoint uses form data; use the email address as `username`.

```bash
TOKEN=$(curl --silent --request POST "$BASE_URL/auth/login" \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "username=$EMAIL" \
  --data-urlencode "password=$PASSWORD" \
  | jq --raw-output '.access_token')
```

### Profiles

All profile endpoints require an `Authorization: Bearer` token.

#### Create a profile

`POST /profiles` — Create a profile with an optional resume upload, GitHub
username, and portfolio URL.

```bash
PROFILE_ID=$(curl --silent --request POST "$BASE_URL/profiles" \
  --header "Authorization: Bearer $TOKEN" \
  --form 'github_username=octocat' \
  --form 'portfolio_url=https://example.com' \
  | jq --raw-output '.id')
```

All fields are optional. To upload a resume, add a `resume_file` form field.
PDF, Markdown, and plain-text files are accepted; any other type returns `422`.

```bash
curl --request POST "$BASE_URL/profiles" \
  --header "Authorization: Bearer $TOKEN" \
  --form 'github_username=octocat' \
  --form 'resume_file=@/path/to/resume.md;type=text/markdown'
```

#### Retrieve a profile

`GET /profiles/{profile_id}` — Retrieve a profile owned by the authenticated
user.

```bash
curl --header "Authorization: Bearer $TOKEN" \
  "$BASE_URL/profiles/$PROFILE_ID"
```

#### Update a profile

`PUT /profiles/{profile_id}` — Update a profile's GitHub username or portfolio
URL.

```bash
curl --request PUT "$BASE_URL/profiles/$PROFILE_ID" \
  --header "Authorization: Bearer $TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{"github_username":"octocat","portfolio_url":"https://example.com"}'
```

### Reviews

All review endpoints require an `Authorization: Bearer` token. Create a review
before trying the retrieval or status examples.

#### Request a review

`POST /reviews` — Request a portfolio review for a profile. It returns a
review with `status` set to `pending` while processing runs in the background.

```bash
REVIEW_ID=$(curl --silent --request POST "$BASE_URL/reviews" \
  --header "Authorization: Bearer $TOKEN" \
  --header 'Content-Type: application/json' \
  --data "{\"profile_id\": \"$PROFILE_ID\"}" \
  | jq --raw-output '.id')
```

#### Retrieve a review

`GET /reviews/{review_id}` — Retrieve a completed or in-progress review.

```bash
curl --header "Authorization: Bearer $TOKEN" \
  "$BASE_URL/reviews/$REVIEW_ID"
```

#### Check review status

`GET /reviews/{review_id}/status` — Retrieve a review's current status and
progress percentage.

```bash
curl --header "Authorization: Bearer $TOKEN" \
  "$BASE_URL/reviews/$REVIEW_ID/status"
```

#### List reviews

`GET /reviews` — List the authenticated user's reviews. `page` defaults to 1
and `page_size` defaults to 20. A `page` below 1 is treated as 1, and a
`page_size` outside 1–100 falls back to 20.

```bash
curl --header "Authorization: Bearer $TOKEN" \
  "$BASE_URL/reviews?page=1&page_size=20"
```

### Cleaning up

#### Delete a profile

`DELETE /profiles/{profile_id}` — Delete a profile and its associated data,
including its reviews. Returns `204 No Content`.

Run this last: afterwards, the profile and review examples above return `404`
for the deleted IDs.

```bash
curl --include --request DELETE "$BASE_URL/profiles/$PROFILE_ID" \
  --header "Authorization: Bearer $TOKEN"
```

## Interactive Docs

When the API is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
