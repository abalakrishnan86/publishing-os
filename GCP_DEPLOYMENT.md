# GCP Deployment Guide — Publishing OS

Deploys two Cloud Run services (backend + frontend) and one Cloud SQL PostgreSQL instance.

```
publishing-os/
├── backend/    → Cloud Run service (FastAPI)
├── frontend/   → Cloud Run service (Next.js)
└── Cloud SQL   → PostgreSQL 15
```

---

## Prerequisites

- GCP account with billing enabled
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated
- Docker installed locally
- Your `ANTHROPIC_API_KEY`

---

## Step 1 — GCP Project Setup

```bash
# Create a new project (or use an existing one)
gcloud projects create publishing-os-prod --name="Publishing OS"
gcloud config set project publishing-os-prod

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

---

## Step 2 — Artifact Registry (Docker image storage)

```bash
gcloud artifacts repositories create publishing-os \
  --repository-format=docker \
  --location=us-central1 \
  --description="Publishing OS images"

# Authenticate Docker to push images
gcloud auth configure-docker us-central1-docker.pkg.dev
```

---

## Step 3 — Cloud SQL (PostgreSQL)

```bash
# Create the instance (takes ~5 minutes)
gcloud sql instances create publishing-os-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-size=10GB \
  --storage-type=SSD

# Create the database
gcloud sql databases create publishing_os \
  --instance=publishing-os-db

# Create a user
gcloud sql users create appuser \
  --instance=publishing-os-db \
  --password=YOUR_DB_PASSWORD
```

> Note your **instance connection name** — you'll need it below:
> ```bash
> gcloud sql instances describe publishing-os-db --format="value(connectionName)"
> # Example output: publishing-os-prod:us-central1:publishing-os-db
> ```

---

## Step 4 — Secret Manager

Store sensitive values so they never appear in container images or Cloud Run env vars in plaintext.

```bash
# Anthropic API key
echo -n "YOUR_ANTHROPIC_API_KEY" | \
  gcloud secrets create ANTHROPIC_API_KEY --data-file=-

# Database password
echo -n "YOUR_DB_PASSWORD" | \
  gcloud secrets create DB_PASSWORD --data-file=-

# Grant Cloud Run access to secrets
gcloud projects add-iam-policy-binding publishing-os-prod \
  --member="serviceAccount:$(gcloud projects describe publishing-os-prod --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Step 5 — Backend (FastAPI) Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Cloud SQL connector
RUN pip install cloud-sql-python-connector[pg8000] pg8000

COPY app/ ./app/

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Update `backend/app/config.py` for Cloud SQL

Add this connection logic alongside your existing config:

```python
# In config.py, the DATABASE_URL env var will be set by Cloud Run.
# For Cloud SQL, use the format:
# postgresql+pg8000://USER:PASS@/DB?unix_sock=/cloudsql/INSTANCE_CONNECTION_NAME/.s.PGSQL.5432
```

---

## Step 6 — Deploy Backend to Cloud Run

```bash
# Build and push the image
cd backend
docker build -t us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/backend:latest .
docker push us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/backend:latest

# Deploy to Cloud Run
gcloud run deploy publishing-os-backend \
  --image=us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/backend:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --add-cloudsql-instances=publishing-os-prod:us-central1:publishing-os-db \
  --set-env-vars="DATABASE_URL=postgresql+pg8000://appuser:YOUR_DB_PASSWORD@/publishing_os?unix_sock=/cloudsql/publishing-os-prod:us-central1:publishing-os-db/.s.PGSQL.5432" \
  --set-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest" \
  --set-env-vars="UPLOAD_DIR=/tmp/uploads,MAX_FILE_SIZE_MB=10" \
  --memory=512Mi \
  --min-instances=0 \
  --max-instances=5
```

> After deploy, note the backend URL — looks like:
> `https://publishing-os-backend-xxxx-uc.a.run.app`

---

## Step 7 — Frontend (Next.js) Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .

# Set the backend URL at build time
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# Production image
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
```

### Enable standalone output in `frontend/next.config.mjs`

```js
const nextConfig = {
  output: 'standalone',   // add this line
};
export default nextConfig;
```

---

## Step 8 — Deploy Frontend to Cloud Run

Replace `BACKEND_URL` with the URL from Step 6.

```bash
cd frontend

# Build with backend URL baked in
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://publishing-os-backend-xxxx-uc.a.run.app \
  -t us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/frontend:latest .

docker push us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/frontend:latest

# Deploy to Cloud Run
gcloud run deploy publishing-os-frontend \
  --image=us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/frontend:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --port=3000 \
  --memory=512Mi \
  --min-instances=0 \
  --max-instances=3
```

> The frontend URL will be your public app URL:
> `https://publishing-os-frontend-xxxx-uc.a.run.app`

---

## Step 9 — Run DB Migrations

After the backend is deployed, run Alembic migrations via a one-off Cloud Run job:

```bash
gcloud run jobs create run-migrations \
  --image=us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/backend:latest \
  --region=us-central1 \
  --add-cloudsql-instances=publishing-os-prod:us-central1:publishing-os-db \
  --set-env-vars="DATABASE_URL=postgresql+pg8000://appuser:YOUR_DB_PASSWORD@/publishing_os?unix_sock=/cloudsql/publishing-os-prod:us-central1:publishing-os-db/.s.PGSQL.5432" \
  --command="alembic" \
  --args="upgrade,head"

gcloud run jobs execute run-migrations --region=us-central1 --wait
```

---

## Summary

| Component | Service | URL |
|---|---|---|
| Frontend | Cloud Run | `https://publishing-os-frontend-xxxx-uc.a.run.app` |
| Backend API | Cloud Run | `https://publishing-os-backend-xxxx-uc.a.run.app` |
| Database | Cloud SQL (PostgreSQL 15) | Internal via Unix socket |
| Secrets | Secret Manager | `ANTHROPIC_API_KEY` |

---

## Estimated Cost (low traffic)

| Service | Free Tier | Beyond Free |
|---|---|---|
| Cloud Run | 2M req/mo free | ~$0.40 per million req |
| Cloud SQL (db-f1-micro) | None | ~$7–10/mo |
| Artifact Registry | 0.5 GB free | $0.10/GB |

**Total at low traffic: ~$7–10/mo** (dominated by Cloud SQL).

To reduce cost further: pause the Cloud SQL instance when not in use, or use **Supabase** (free managed Postgres) with Cloud Run.

---

## Redeploying After Code Changes

```bash
# Backend
docker build -t us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/backend:latest ./backend
docker push us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/backend:latest
gcloud run deploy publishing-os-backend --image=us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/backend:latest --region=us-central1

# Frontend
docker build --build-arg NEXT_PUBLIC_API_URL=https://publishing-os-backend-xxxx-uc.a.run.app \
  -t us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/frontend:latest ./frontend
docker push us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/frontend:latest
gcloud run deploy publishing-os-frontend --image=us-central1-docker.pkg.dev/publishing-os-prod/publishing-os/frontend:latest --region=us-central1
```
