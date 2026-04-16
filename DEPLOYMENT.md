# QAMini Deployment Guide

## Vercel Deployment

### Option 1: Deploy Frontend to Vercel (Recommended for Quick Start)

The frontend can be deployed directly to Vercel with automatic deployments from GitHub.

#### Steps:

1. **Go to Vercel**
   - Visit https://vercel.com
   - Sign up or log in with GitHub

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select the QAMini repository from GitHub
   - Click "Import"

3. **Configure Project**
   - Framework Preset: **Vite**
   - Root Directory: **frontend**
   - Build Command: **npm run build**
   - Output Directory: **dist**
   - Install Command: **npm install**

4. **Environment Variables** (Optional)
   - `VITE_API_BASE`: URL of your backend API (e.g., `https://your-backend.com`)
   - If not set, defaults to `http://localhost:8000`

5. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically

### Option 2: Full Stack on Vercel (Frontend + Backend API Functions)

Deploy both frontend and backend on Vercel using serverless functions.

#### Prerequisites:
- Vercel CLI: `npm install -g vercel`
- Node.js and Python 3.9+

#### Steps:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Local**
   ```bash
   cd qamini
   vercel
   ```
   - Follow the prompts
   - Select the GitHub account
   - Confirm project settings

4. **Connect GitHub for Auto-Deployment**
   - In Vercel Dashboard, go to Project Settings
   - Connect to GitHub
   - Enable automatic deployments on push to main

#### Limitations with This Approach:
- Python serverless functions on Vercel have coldstart delays
- File uploads and data processing are limited by function timeout (10s on free tier)
- Suitable for demo/prototype purposes

### Option 3: Separate Backend Deployment (Recommended for Production)

Deploy frontend to Vercel and backend to a separate service.

#### Recommended Backend Services:
1. **Railway** - Easy Python/FastAPI deployment
2. **Render** - Free tier available
3. **Heroku** - Classic choice (paid)
4. **AWS Lambda** - Serverless with S3 file storage
5. **DigitalOcean App Platform** - Full control

#### Steps:

**A. Deploy Backend to Railway:**

1. Go to https://railway.app
2. Create new project → Deploy from GitHub
3. Select QAMini repository
4. In project settings:
   - Select `backend` as root directory
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable if needed
6. Deploy

**B. Update Frontend to Use Backend URL:**

1. In Vercel Dashboard, go to Project Settings
2. Go to Environment Variables
3. Add: `VITE_API_BASE=https://your-railway-app.railway.app`
4. Re-deploy frontend

#### Deploy Backend to Railway via CLI:

```bash
npm install -g @railway/cli
railway login
cd backend
railway up
```

### Option 4: Docker Deployment

Deploy using Docker containers to any service supporting Docker.

#### Build Docker Image:

```bash
docker build -t qamini-backend:latest -f backend/Dockerfile .
docker build -t qamini-frontend:latest -f frontend/Dockerfile .
```

#### Services supporting Docker:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Railway (supports Dockerfile)

---

## Post-Deployment Configuration

### 1. Update API URL
If deploying frontend and backend separately, set the backend URL:

For Vercel Frontend:
```
Environment Variable: VITE_API_BASE
Value: https://your-backend-url.com
```

### 2. Configure CORS
The backend already has CORS enabled for all origins. For production, update:

In `backend/main.py`:
```python
allow_origins=["https://your-frontend-domain.vercel.app"]
```

### 3. Test Deployment

```bash
# Test health endpoint
curl https://your-backend-url.com/api/health

# Test upload endpoint
curl -X POST https://your-backend-url.com/api/upload \
  -F "file=@community.csv"
```

---

## Performance Optimization

### For Vercel Functions Backend:

1. **Increase timeout** (paid plans):
   - Free: 10 seconds
   - Pro: 60 seconds
   - Enterprise: Up to 900 seconds

2. **Use Web Analytics**:
   - Monitor slow endpoints in Vercel Analytics
   - Optimize hot paths

3. **Cache Strategy**:
   - Consider caching experiment results
   - Pre-compute common queries

### For Production:

1. **Database**: Migrate from CSV to PostgreSQL
2. **Caching**: Add Redis for embeddings cache
3. **CDN**: Images and static assets via Vercel Edge Network
4. **Monitoring**: Add Sentry or similar for error tracking

---

## Troubleshooting

### Issue: Backend functions timing out
**Solution**: 
- Reduce dataset size
- Deploy backend separately to Railway/Render
- Use paid Vercel tier with longer timeout

### Issue: `CORS` errors
**Solution**:
- Check `API_BASE` URL in frontend `.env`
- Ensure backend CORS includes frontend origin
- Use Vercel proxy rewrite (if backend is on same domain)

### Issue: Large file uploads failing
**Solution**:
- Vercel has 4.5MB limit for function payloads
- Consider chunked uploads
- Deploy backend to service with higher limits

### Issue: Cold starts too slow
**Solution**:
- Use a persistent backend service (Railway, Render)
- Implement response caching
- Use Vercel's edge functions for static content

---

## Free Tier Limitations

**Vercel (Frontend):**
- Unlimited deployments
- Edge Network included
- 10 seconds function timeout
- 4.5MB request/response size

**Railway (Backend Alternative):**
- $5/month free credits
- ~300 hours/month runtime
- Good for documentation and demos

---

## One-Click Deployment

### Deploy to Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/tanishq-fig/QAmini&project-name=qamini&repo-name=QAmini&env=VITE_API_BASE&envDescription=Backend%20API%20URL&envLink=https://railway.app)

---

## Support

For deployment issues:
1. Check Vercel Documentation: https://vercel.com/docs
2. Check Railway Documentation: https://railway.app/docs
3. Review GitHub Issues in the repository
4. Check backend logs in Vercel/Railway dashboard

---

**Happy Deploying! 🚀**
