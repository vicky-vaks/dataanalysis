# Deployment Guide for AI Job Market Project

> [!IMPORTANT]
> **Split Deployment Strategy**
> Due to the large size of the AI models (>500MB unzipped), the backend **CANNOT** run on Vercel's free serverless functions (limit 250MB).
>
> **You MUST deploy:**
> 1.  **Frontend** -> **Vercel**
> 2.  **Backend** -> **Render**

---

## Part 1: Deploy Backend to Render (Free Web Service)

1.  Push your latest code to GitHub.
2.  Go to [Render Dashboard](https://dashboard.render.com/).
3.  Click **New +** -> **Web Service**.
4.  Connect your repository.
5.  **Settings:**
    -   **Name:** `ai-job-market-api`
    -   **Runtime:** `Python 3`
    -   **Start Command:** Render should auto-detect the `Procfile` (`web: gunicorn src.api.flask_app:app`). If not, enter that command manually.
6.  **Environment Variables:**
    -   `PYTHON_VERSION`: `3.9.0`
7.  Click **Create Web Service**.
8.  **Wait** for it to deploy (it make take 5-10 minutes).
9.  **COPY the URL** (e.g., `https://ai-job-market-api.onrender.com`).

---

## Part 2: Deploy Frontend to Vercel

1.  Go to [Vercel Dashboard](https://vercel.com/dashboard).
2.  Import your repository.
3.  **Framework Preset:** Vite (should auto-detect).
4.  **Root Directory:** `frontend` (Edit the root directory setting).
5.  **Environment Variables (CRITICAL):**
    -   **Name:** `VITE_API_BASE`
    -   **Value:** Paste your Render Backend URL from Part 1 (e.g., `https://ai-job-market-api.onrender.com`).
    -   *Note: Do not add a trailing slash.*
6.  Click **Deploy**.

---

## Part 3: Verification

1.  Open your deployed Vercel URL.
2.  Look at the sidebar bottom: `API: https://ai-job-market-api.onrender.com`.
    -   If it says `/api`, you missed the Environment Variable in Step 5. Redeploy!
3.  Upload a CSV.
    -   It should work! (Note: Initial "Cold Start" on Render might take 50 seconds to wake up).

---

## Local Development (Bonus)

-   Frontend: `npm run dev` (Runs on `localhost:5173`)
-   Backend: `gunicorn src.api.flask_app:app` (Runs on `localhost:8000`)
-   The local proxy in `vite.config.js` will verify everything works locally.
