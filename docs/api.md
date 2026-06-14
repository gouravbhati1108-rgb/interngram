# Interngram API

Base URL: `http://localhost:8000/api/v1`

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register student or company |
| POST | `/auth/login` | Login, sets httpOnly cookies |
| POST | `/auth/mfa/verify` | Admin MFA verification |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Clear session cookies |

## Students

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/students/me` | Get profile |
| PATCH | `/students/me` | Update profile |
| POST | `/students/resume/upload-url` | Get presigned S3 upload URL |
| GET | `/students/applications` | List applications |
| POST | `/students/applications/{id}` | Apply to internship |
| POST | `/students/verification/upload-url` | Presigned URL for verification docs |
| POST | `/students/verification` | Submit verification document |

## Companies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/companies/me` | Company profile |
| PATCH | `/companies/me` | Update profile |
| POST | `/companies/internships` | Create internship |
| GET | `/companies/applications` | List applicants |
| PATCH | `/companies/applications/{id}` | Update applicant status |
| GET | `/companies/analytics` | Dashboard analytics |

## Internships

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/internships` | Search/list internships |
| GET | `/internships/{id}` | Internship details |

## Reviews

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reviews/company/{id}` | List approved reviews |
| POST | `/reviews` | Submit review (verified intern only) |
| GET | `/reviews/eligibility/{company_id}` | Check review eligibility |

## Rankings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rankings` | Leaderboard |
| GET | `/rankings/company/{id}` | Company ranking breakdown |

## Discussions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/discussions/company/{slug}` | List posts |
| POST | `/discussions/company/{slug}` | Create post |
| GET | `/discussions/posts/{id}/comments` | List comments |
| POST | `/discussions/posts/{id}/comments` | Add comment |
| POST | `/discussions/report` | Report abuse |

## Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications` | List notifications |
| PATCH | `/notifications/{id}/read` | Mark as read |

## Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | User management |
| GET | `/admin/companies/pending` | Pending company verifications |
| PATCH | `/admin/companies/{id}/verify` | Approve/reject company |
| GET | `/admin/verifications/pending` | Pending intern verifications |
| PATCH | `/admin/verifications/{id}` | Approve/reject intern docs |
| GET | `/admin/reviews/pending` | Review moderation queue |
| PATCH | `/admin/reviews/{id}` | Moderate review |
| GET | `/admin/reports` | Complaint queue |
| GET | `/admin/audit-logs` | Audit trail |
| GET | `/admin/rankings` | Ranking monitor |

## Security

- JWT access tokens (15 min) + refresh tokens (7 days, httpOnly cookies)
- CSRF: send `X-CSRF-Token` header matching `csrf_token` cookie on mutating requests
- Rate limiting on auth endpoints
- Argon2 password hashing
- Admin MFA required
