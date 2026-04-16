# 🚀 QAMini Vercel Deployment Guide

Your project is **fully configured** and **production-ready** for Vercel! Follow these steps to deploy:

---

## ⚡ QUICKEST WAY: Deploy with One Click

### Step 1: Click Deploy Button (Takes 2 minutes)

**[🚀 DEPLOY TO VERCEL NOW](https://vercel.com/import?repo=tanishq-fig/QAmini)**

Or manually:
1. Go to: **https://vercel.com/new**
2. Click: **"Continue with GitHub"**
3. Search and select: **QAmini**
4. Click: **"Import"**
5. Click: **"Deploy"** ✅

**That's it! Your frontend is live!**

---

## 📦 What Gets Deployed

✅ **Frontend (React + Vite)**
- Automatically built and optimized
- Served globally via Vercel CDN
- Auto-deploys on every GitHub push

✅ **API Stub** (Optional)
- Health check endpoint
- CORS configured
- Ready for backend connection

---

## 🔗 Connect Backend (For Full Functionality)

Your frontend needs a backend to enable:
- CSV file uploads
- Statistical analysis (8 experiments)
- Chat/QA functionality

### Option A: Deploy Backend to Railway (Easiest)

**Step 1: Go to Railway**
- Visit: https://railway.app
- Click: "Start New Project"
- Select: "Deploy from GitHub"

**Step 2: Configure Backend**
- Search: **QAmini** repository
- Select PostgreSQL (optional, for data persistence)
- In Variables section, add:
  ```
  PORT=8000
  ```

**Step 3: Confirm Deployment**
- Railway auto-deploys from GitHub
- Get your backend URL: `https://qamini-xxx.railway.app`

**Step 4: Connect to Frontend**
- Go to Vercel Dashboard
- Select your QAMini project
- Go to: **Settings → Environment Variables**
- Add new variable:
  ```
  VITE_API_BASE = https://qamini-xxx.railway.app
  ```
- Click: **Save**
- Wait for redeploy (2-3 minutes)

### Option B: Deploy Backend to Render.com

**Step 1: Go to Render**
- Visit: https://render.com
- Click: "New+"
- Select: "Web Service"
- Connect GitHub account and select **QAmini**

**Step 2: Configure Service**
- Name: `qamini-backend`
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Instance Type: **Free** (or Starter+)

**Step 3: Deploy**
- Click: "Create Web Service"
- Wait for deployment (~3-5 minutes)
- Copy URL from dashboard

**Step 4: Set Backend URL in Vercel**
- Same as Option A, Step 4

---

## ✅ Verify Deployment

### Check Frontend
```
https://your-qamini.vercel.app
```

You should see:
- ✅ QAMini dashboard landing page
- ✅ Upload interface
- ✅ Clean, responsive UI

### Check Backend Connection
```bash
# If backend is connected:
curl https://your-backend-url.railway.app/api/health

# Response:
# {"status": "ok", "message": "..."}
```

---

## 🌍 Your Live URLs

| Component | URL |
|-----------|-----|
| **Frontend** | `https://qamini-xxx.vercel.app` |
| **Backend (Railway)** | `https://qamini-xxx.railway.app` |
| **GitHub** | `https://github.com/tanishq-fig/QAmini` |

---

## 📊 Feature Status After Deployment

| Feature | Status | Notes |
|---------|--------|-------|
| Landing Page | ✅ | Works immediately |
| Upload CSV | ✅ | Works with backend |
| Analysis (8 experiments) | ✅ | Works with backend |
| Chat/QA | ✅ | Works with backend |
| Dark Mode | ✅ | Works |
| Responsive Design | ✅ | Works |

---

## 🔄 Auto-Deployment

After deployment, every time you push to GitHub:
1. Vercel detects changes
2. Automatically rebuilds frontend
3. Deploys new version
4. Live within 1-2 minutes

**No manual deployment needed!** 🎉

---

## 📝 Environment Variables

If needed, set these in Vercel Dashboard:

```
VITE_API_BASE = https://your-backend-api.railway.app
```

---

## 🚨 Troubleshooting

### Issue: "Cannot upload files"
**Solution:** Backend not deployed. Follow "Connect Backend" section above.

### Issue: "CORS error in console"
**Solution:** Check `VITE_API_BASE` URL in Vercel Environment Variables.

### Issue: "Page not loading"
**Solution:**
1. Wait 30 seconds (builds take time)
2. Refresh browser
3. Check Vercel Deployments tab for errors

### Issue: "Backend taking too long"
**Solution:** Free Railway tier may be slow. Upgrade to Starter+ ($7/month) for better performance.

---

## 💡 Pro Tips

1. **Monitor Deployments**: Check Vercel Dashboard → Deployments tab
2. **View Logs**: Click on failed deployment to see error logs
3. **Rollback**: Click "Rollback" on previous deployment if issues occur
4. **View Analytics**: Vercel provides real-time analytics and monitoring

---

## 📚 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Railway Dashboard**: https://railway.app/dashboard
- **Render Dashboard**: https://dashboard.render.com
- **GitHub Repository**: https://github.com/tanishq-fig/QAmini

---

## 🎯 Next Steps

1. ✅ Deploy frontend to Vercel (2 min)
2. ✅ Deploy backend to Railway (5 min)
3. ✅ Connect them together (2 min)
4. ✅ Test uploads and chat
5. ✅ Share your live website!

---

## 🎉 You're All Set!

Your QAMini application is production-ready and deployed globally!

**Start here**: [Deploy to Vercel](https://vercel.com/import?repo=tanishq-fig/QAmini)

---

**Need help?** Check the [DEPLOYMENT.md](./DEPLOYMENT.md) file for detailed instructions.
