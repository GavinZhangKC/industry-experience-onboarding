# Vercel deployment

The repository deploys as two Vercel projects. AWS deployment files remain in
place, and Aurora PostgreSQL remains in AWS.

## 1. Create the frontend project

Import this GitHub repository in Vercel and configure:

- Root Directory: `frontend`
- Framework Preset: Vite
- Production Branch: `integration` while this branch is being tested
- Environment variable: `VITE_API_BASE_URL` = the backend Vercel URL

The first deployment can be created before the backend URL is known, then
redeployed after the variable is added.

## 2. Create the backend project

Import the same GitHub repository a second time and configure:

- Root Directory: `backend`
- Framework Preset: Other (FastAPI is detected from `main.py`)
- Production Branch: `integration` while this branch is being tested

Copy the variable names from `backend/.env.vercel.example` into the project's
Environment Variables page. Required production values are:

```text
DATA_BACKEND=aurora
AURORA_AWS_REGION=ap-southeast-2
DB_CLUSTER_ARN=<existing Aurora cluster ARN>
DB_SECRET_ARN=<existing Secrets Manager secret ARN>
DB_NAME=postgres
AWS_ACCESS_KEY_ID=<dedicated IAM access key>
AWS_SECRET_ACCESS_KEY=<dedicated IAM secret key>
MAPS_PROVIDER=mock
ALLOWED_ORIGINS=https://<frontend-project>.vercel.app
```

Do not prefix backend-only variables with `VITE_`; Vite exposes variables with
that prefix to browser code.

For the MVP credential setup, use a dedicated IAM identity with only the
permissions needed by this read-only backend:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "rds-data:ExecuteStatement",
      "Resource": "<existing Aurora cluster ARN>"
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "<existing Secrets Manager secret ARN>"
    }
  ]
}
```

The key values belong only in Vercel's Environment Variables page, never in
Git. AWS/Vercel OIDC with short-lived credentials is the preferred later
hardening step; it is not required for the initial deployment.

## 3. Connect and verify

After both production deployments finish:

1. Set the frontend `VITE_API_BASE_URL` to the backend production URL.
2. Set backend `ALLOWED_ORIGINS` to the frontend production origin.
3. Redeploy both projects so the new variables take effect.
4. Open `<backend-url>/health`.
5. Test `POST <backend-url>/api/v1/routes`.
6. Test `GET <backend-url>/api/v1/quiet-spaces`.
7. Open the frontend and test route generation and quiet-space search.

Preview deployments use changing origins. Add a specific preview origin to
`ALLOWED_ORIGINS` when testing a preview; do not change production CORS to `*`.

## What remains on AWS

- Aurora PostgreSQL and Secrets Manager
- RDS Data API
- Node F4 ingestion scripts and any future scheduled ingestion job
- `template.yaml` and `backend/lambda_handlers/` for the AWS deployment option
