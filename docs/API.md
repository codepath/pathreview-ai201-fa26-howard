# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### Health

`GET /health` — Returns service status and dependency health.

**Example Request (cURL):**

```bash
curl -X GET "http://localhost:8000/health" \
  -H "accept: application/json"
```

Returns `200 OK` when all dependencies are healthy or `503 Service Unavailable` when one or more dependencies are unhealthy.

### Authentication

`POST /auth/register` — Create a new account.

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepassword123"
  }'
```

`POST /auth/login` — Obtain a JWT access token.

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=user1@example.com&password=password1"
```

The response includes an `access_token` and `token_type`. Use the access token to authenticate requests to protected endpoints.

For the following examples, replace `YOUR_ACCESS_TOKEN` with the token returned by login.

```bash
TOKEN="YOUR_ACCESS_TOKEN"
```

### Profiles

`POST /profiles` — Create a profile with resume and GitHub username.

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/profiles" \
  -H "Authorization: Bearer $TOKEN" \
  -F "github_username=your-github-username" \
  -F "portfolio_url=https://yourportfolio.com"
```

To include a resume, add the following form field:

```bash
-F "resume_file=@/path/to/resume.pdf"
```

`GET /profiles/{profile_id}` — Retrieve a profile.

**Example Request (cURL):**

```bash
curl -X GET "http://localhost:8000/profiles/PROFILE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

`PUT /profiles/{profile_id}` — Update a profile.

**Example Request (cURL):**

```bash
curl -X PUT "http://localhost:8000/profiles/PROFILE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "github_username": "updated-username",
    "portfolio_url": "https://updatedportfolio.com"
  }'
```

`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

**Example Request (cURL):**

```bash
curl -X DELETE "http://localhost:8000/profiles/PROFILE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/reviews" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "PROFILE_ID"
  }'
```

`GET /reviews/{review_id}` — Retrieve a completed review.

**Example Request (cURL):**

```bash
curl -X GET "http://localhost:8000/reviews/REVIEW_ID" \
  -H "Authorization: Bearer $TOKEN"
```

`GET /reviews` — List reviews for the authenticated user (paginated).

**Example Request (cURL):**

```bash
curl -X GET "http://localhost:8000/reviews?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
```

`GET /reviews/{review_id}/status` — Retrieve the status and progress of a review.

**Example Request (cURL):**

```bash
curl -X GET "http://localhost:8000/reviews/REVIEW_ID/status" \
  -H "Authorization: Bearer $TOKEN"
```

## Interactive Docs

When the API is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
