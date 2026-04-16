# QAMini Deployment Complete - Final Setup Guide

## ✅ What's Deployed

### Frontend - Vercel (Live)
- **URL**: https://frontend-iota-hazel-11.vercel.app
- **Status**: ✅ Deployed and running
- **Technology**: React 18 + Vite + Tailwind CSS

### Backend - Ready for Render Deployment
- **Current Status**: 🟡 Ready to deploy, needs Render setup
- **Technology**: FastAPI + Python 3.10
- **GitHub**: https://github.com/tanishq-fig/QAmini
- **Configuration**: render.yaml created

---

## 📋 Complete Backend Deployment on Render.com

### Step 1: Create Render Account & Connect GitHub
1. Visit https://render.com
2. Sign up with your GitHub account or email
3. Click "Dashboard" → "New Web Service"
4. Select "Build and deploy from a Git repository"
5. Connect your GitHub account when prompted
6. Search for "QAmini" repository

### Step 2: Configure the Service
When creating the new Web Service:
- **Name**: `qamini-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Instance Type**: Free (sufficient for testing/demo)

### Step 3: Add Environment Variables
In the Render dashboard, scroll to "Environment Variables" and add:
```
DATABASE_URL = sqlite:///./argo.db
CORS_ORIGINS = https://frontend-iota-hazel-11.vercel.app
```

### Step 4: Deploy
- Click "Create Web Service"
- Render will automatically fetch from GitHub and deploy
- Wait 3-5 minutes for deployment to complete
- Once deployed, you'll see your service URL (e.g., `https://qamini-backend.onrender.com`)

### Step 5: Update Frontend with Backend URL
Once your Render backend is deployed:

1. **Get your backend URL** from Render dashboard
2. Go to https://vercel.com/dashboard → Select "frontend"
3. Navigate to "Settings" → "Environment Variables"
4. Add a new variable:
   - **Name**: `VITE_API_BASE`
   - **Value**: `https://your-render-backend-url.onrender.com` (e.g., `https://qamini-backend.onrender.com`)
5. **Redeploy**: Click "Deployments" → Find latest deployment → Click "Redeploy"

---

## 🧪 Testing the Complete System

After all deployments and environment variables are set:

1. **Open frontend**: https://frontend-iota-hazel-11.vercel.app
2. **Upload test data**: Use `community.csv` from the repo
3. **Verify analysis results**: Should show 8 experiments with statistical results
4. **Test chat/QA**: Ask questions like "What is the mean temperature?" 
5. **Check browser console** (F12): Should show no CORS errors

---

## ⚙️ What Each Part Does

### Frontend (Vercel)
- Handles user interface (upload, analysis viewing, chat)
- Uses environment variable `VITE_API_BASE` to connect to backend
- No database needed - stateless

### Backend (Render)
- Processes CSV files and runs 8 statistical experiments
- Builds semantic search (FAISS) for QA functionality
- Stores data temporarily (SQLite in memory/mounts)
- Returns analysis results and answers to frontend

---

## 🔗 Quick Reference URLs

| Component | URL | Status |
|-----------|-----|--------|
| **Frontend** | https://frontend-iota-hazel-11.vercel.app | ✅ Live |
| **GitHub** | https://github.com/tanishq-fig/QAmini | ✅ Synced |
| **Backend** | https://your-render-url.onrender.com | 🟡 Pending (follow steps above) |

---

## 📝 Local Development (if needed)

To run locally for testing:

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
# Runs on http://localhost:8000
```

### Frontend  
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5174
```

---

## 🆘 Troubleshooting

### If frontend shows "API connection error":
1. Check browser console (F12) for actual error message
2. Verify `VITE_API_BASE` environment variable is set on Vercel
3. Check Render backend logs for errors
4. Verify CORS_ORIGINS matches the Vercel URL

### If Render deployment fails:
1. Check Render dashboard → Logs for error details
2. Verify `backend/requirements.txt` exists and is valid
3. Ensure Python 3.10 build command syntax is correct
4. Check free-tier limitations (512MB RAM limit)

### If chat isn't working:
1. Ensure backend is actually deployed on Render
2. Check that semantic search (FAISS) initialized correctly
3. Look at Render logs for "FAISS index" or "embedding" errors

---

## 🎉 You're Done!

The entire QAMini application is now:
- ✅ Deployed to production (Vercel frontend)
- ✅ Configured for backend scaling (Render backend)
- ✅ Version-controlled on GitHub  
- ✅ Ready for user testing

**Total deployment time**: ~15-20 minutes (mostly Render initialization)

---

**Need help?** Check the individual module READMEs in `frontend/README.md` and the requirements in `backend/requirements.txt`.
