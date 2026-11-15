# Q-Play Deployment Guide

This guide covers all deployment strategies for the **Q-Play Tic-Tac-Toe Reinforcement Learning Platform**:
- **Strategy 1:** Free Cloud One-Click Deploy (Render.com, Railway, Hugging Face Spaces)
- **Strategy 2:** Docker / Container Deployment (AWS, GCP, DigitalOcean, Fly.io, Self-Hosted)
- **Strategy 3:** Jamstack Split Deploy (Vercel / Netlify + Backend Web Service)
- **Strategy 4:** Local / On-Premise Host (Windows / Linux systemd / PM2)

---

## Architecture Overview
The platform is built as a unified full-stack application:
- **Backend:** FastAPI + Uvicorn + NumPy (Python 3.11+)
- **Frontend:** React 19 + TypeScript + Vite
- **Static Hosting:** In production, FastAPI automatically serves the built frontend (`frontend/dist`) at root `/`. This means you can deploy the entire application as a **single web service** on a single port!

---

## Strategy 1: Free Cloud Deploy (Render.com) — *Recommended & Easiest*

Render offers free web service hosting and natively supports Docker or Python:

### Step 1: Push project to GitHub
```bash
git init
git add .
git commit -m "Initial commit of Q-Play RL platform"
git remote add origin https://github.com/YOUR_USERNAME/q-play-rl.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [https://dashboard.render.com](https://dashboard.render.com) and sign in.
2. Click **New +** &rarr; **Web Service**.
3. Connect your GitHub repository `q-play-rl`.
4. Choose **Docker** as the Environment (Render will automatically detect our multi-stage `Dockerfile`).
5. Choose the **Free** tier.
6. Click **Create Web Service**.
7. Render will build the React frontend and deploy the FastAPI backend. You will receive a live URL: `https://q-play-rl.onrender.com`.

---

## Strategy 2: Docker / Container Deployment (Universal)

The included [Dockerfile](file:///C:/Users/naruj/OneDrive/Desktop/obv%20projects/ai/Dockerfile) is multi-stage:
1. Compiles the TypeScript frontend with Node 20.
2. Sets up a slim Python 3.11 environment.
3. Copies backend code and frontend build assets.

### Build and Run with Docker:
```bash
docker build -t q-play-app .
docker run -d -p 8000:8000 --name q-play q-play-app
```
Visit `http://localhost:8000`.

### Run with Docker Compose:
```bash
docker compose up -d
```

---

## Strategy 3: Railway.app Deployment

1. Go to [https://railway.app](https://railway.app).
2. Click **New Project** &rarr; **Deploy from GitHub repo**.
3. Select your repository.
4. Railway will automatically pick up `Dockerfile` and expose the service on a public HTTPS domain.

---

## Strategy 4: Hugging Face Spaces (Free Machine Learning Hosting)

Hugging Face Spaces is an ideal academic hosting platform:
1. Create a new Space at [https://huggingface.co/spaces](https://huggingface.co/spaces).
2. Select **Docker** as the Space SDK.
3. Push your repository files to the Hugging Face Git remote.
4. HF Spaces automatically builds and launches the container for free.

---

## Strategy 5: Split Deploy (Frontend on Vercel + Backend on Render/Fly.io)

If you prefer hosting the React frontend on Vercel or Netlify CDN:

### Deploy Backend:
1. Deploy `backend/` to Render, Railway, or Fly.io.
2. Note your backend URL: e.g., `https://q-play-api.onrender.com`.

### Deploy Frontend to Vercel:
1. Edit `frontend/vercel.json` and replace `https://YOUR-BACKEND-URL.onrender.com` with your real backend URL.
2. In the terminal:
   ```bash
   cd frontend
   npx vercel
   ```

---

## Strategy 6: Local Production Execution (Windows / Mac / Linux)

### Windows:
Double-click `run_local.bat` or run:
```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### Linux / macOS:
```bash
chmod +x run_local.sh
./run_local.sh
```
