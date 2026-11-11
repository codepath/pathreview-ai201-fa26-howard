# API Reference

Base URL: `http://localhost:8000`

Start the application before running these examples:

```bash
make run
```

The authenticated examples use these shell variables. Registering returns an
access token; `jq` extracts it so later commands can send it as a bearer token.

```bash
BASE_URL=http://localhost:8000
EMAIL=developer@example.com
PASSWORD='change-this-password'
```

## Endpoints

### Root

`GET /` — Returns a short service message and the API version.

```bash
curl "$BASE_URL/"
```

### Health

`GET /health` — Returns service status and dependency health.

```bash
curl "$BASE_URL/health"
```

### Authentication

#### Register

`POST /auth/register` — Create a new account and return a JWT access token.

```bash
TOKEN=$(curl --silent --request POST "$BASE_URL/auth/register" \
  --header 'Content-Type: application/json' \
  --data "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
  | jq --raw-output '.access_token')
```

Use a unique email address if the example account already exists.

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

To upload a Markdown or PDF resume, add a `resume_file` form field:

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

#### Delete a profile

`DELETE /profiles/{profile_id}` — Delete a profile and its associated data.

```bash
curl --include --request DELETE "$BASE_URL/profiles/$PROFILE_ID" \
  --header "Authorization: Bearer $TOKEN"
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
and `page_size` defaults to 20 (maximum 100).

```bash
curl --header "Authorization: Bearer $TOKEN" \
  "$BASE_URL/reviews?page=1&page_size=20"
```

## Interactive Docs

When the API is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
