# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### Health

`GET /health` — Returns service status and dependency health.

### Authentication

`POST /auth/register` — Create a new account.
`POST /auth/login` — Obtain a JWT access token.

### Profiles

`POST /profiles`: Create a profile with optional GitHub username, portfolio URL,
and resume upload.

#### Request body: `POST /profiles`

Content type: `multipart/form-data`. Send text fields and the resume file as form
parts, rather than a JSON body. Authentication is required: supply the access
token from `POST /auth/login` in the `Authorization: Bearer <token>` header.

| Field | Type | Required | Description | Example value |
| --- | --- | --- | --- | --- |
| `github_username` | string | No | GitHub username, up to 255 characters. | `janedoe` |
| `portfolio_url` | string | No | Portfolio URL, up to 500 characters. | `https://janedoe.example.com` |
| `resume_file` | file | No | Resume uploaded as a file part. Accepted MIME types are `application/pdf`, `text/markdown`, and `text/plain`. | Contents of a local `resume.md` file with MIME type `text/markdown` |

All three fields may be omitted. To create a profile without a resume, omit the
`resume_file` part. Unsupported upload MIME types are rejected with HTTP 422.

Set `TOKEN` to your access token and replace `./resume.md` with a local UTF-8
Markdown resume file before running this example:

```bash
curl -X POST 'http://localhost:8000/profiles' \
  -H "Authorization: Bearer $TOKEN" \
  -F 'github_username=janedoe' \
  -F 'portfolio_url=https://janedoe.example.com' \
  -F 'resume_file=@./resume.md;type=text/markdown'
```

Let curl set the multipart `Content-Type` header and boundary automatically.
The `@` uploads the file contents; a filename sent as plain text is not a file
upload.

#### Other profile endpoints

`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

### Reviews

`POST /reviews`: Request a new portfolio review for a profile.

#### Request body: `POST /reviews`

Content type: `application/json`. Authentication is required through the same
`Authorization: Bearer <token>` header used for profile creation.

| Field | Type | Required | Description | Example value |
| --- | --- | --- | --- | --- |
| `profile_id` | string (UUID) | Yes | ID of the profile to review. Use the `id` returned when creating your profile. | `123e4567-e89b-12d3-a456-426614174000` |

Example JSON body:

```json
{
  "profile_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

The UUID above illustrates the format. Replace it with the ID of an existing
profile you own. Missing or malformed UUID values are rejected with HTTP 422.
With `TOKEN` set to your access token, send the request as follows:

```bash
curl -X POST 'http://localhost:8000/reviews' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"profile_id":"123e4567-e89b-12d3-a456-426614174000"}'
```

#### Other review endpoints

`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
