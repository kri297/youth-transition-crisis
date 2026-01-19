# Youth Transition Crisis - Aadhaar Analysis

## 🚀 Deployment Guide for Render

### Prerequisites
1. GitHub account
2. Render account (https://render.com - free tier available)
3. This project code

### Step-by-Step Deployment

#### 1. Push Code to GitHub

```bash
# Initialize git (if not already done)
cd c:\Users\HP\Desktop\UIDAI
git init

# Create .gitignore
echo ".venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".DS_Store" >> .gitignore
echo "*.zip" >> .gitignore

# Add all files
git add .
git commit -m "Initial commit - Youth Transition Crisis Analysis"

# Push to GitHub (create new repo first at github.com)
git remote add origin https://github.com/YOUR_USERNAME/youth-crisis-analysis.git
git push -u origin main
```

#### 2. Deploy Backend on Render

1. **Go to Render Dashboard**: https://dashboard.render.com/

2. **Click "New +"** → Select **"Web Service"**

3. **Connect Your Repository**:
   - Click "Connect GitHub" or "Connect GitLab"
   - Select your repository: `youth-crisis-analysis`
   - Click "Connect"

4. **Configure Web Service**:
   - **Name**: `youth-crisis-api` (or any name you prefer)
   - **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (or enter `backend` if needed)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn app_api:app --bind 0.0.0.0:$PORT`

5. **Environment Variables** (Optional):
   - Click "Advanced" → "Add Environment Variable"
   - Add if needed (none required for basic setup)

6. **Instance Type**:
   - Select **"Free"** (0.1 CPU, 512 MB RAM)

7. **Click "Create Web Service"**

8. **Wait for Deployment** (5-10 minutes):
   - Render will install dependencies
   - Start your Flask app
   - You'll get a URL like: `https://youth-crisis-api.onrender.com`

#### 3. Update Frontend API URL

After deployment, update your frontend to use the Render URL:

**Edit `frontend/app.js` line 2:**
```javascript
// Change from:
const API_BASE = 'http://localhost:5000/api';

// To your Render URL:
const API_BASE = 'https://youth-crisis-api.onrender.com/api';
```

#### 4. Host Frontend (Choose One)

**Option A: Netlify (Recommended)**
1. Go to https://www.netlify.com/
2. Drag & drop your `frontend` folder
3. Done! You'll get a URL like: `https://your-site.netlify.app`

**Option B: Vercel**
1. Go to https://vercel.com/
2. Import your GitHub repo
3. Set build settings:
   - Framework Preset: "Other"
   - Root Directory: `frontend`
   - Build Command: (leave empty)
   - Output Directory: `.`
4. Deploy!

**Option C: GitHub Pages**
1. Create `docs/` folder in root
2. Copy all frontend files to `docs/`
3. Push to GitHub
4. Go to repo Settings → Pages
5. Select "Deploy from branch" → `main` → `/docs`
6. Access at: `https://YOUR_USERNAME.github.io/youth-crisis-analysis/`

#### 5. Test Your Deployment

Visit your frontend URL and check:
- ✅ Data loads successfully
- ✅ Charts display properly
- ✅ Navigation works
- ✅ All sections show correct data

### 🔧 Troubleshooting

**Backend not starting?**
- Check Render logs: Dashboard → Your Service → Logs
- Verify all dependencies in `requirements.txt`
- Check data files are included in repo

**CORS errors?**
- Already fixed with `flask-cors` in backend
- Make sure frontend uses correct API URL

**Data not loading?**
- Check API endpoints work: `https://your-api.onrender.com/api/overview`
- Verify data files are in correct paths
- Check browser console for errors

**Free tier limitations:**
- Render free tier spins down after 15 min inactivity
- First request after sleep takes 30-60 seconds
- Upgrade to paid tier for always-on service

### 📝 Important Notes

1. **Data Files**: Make sure data folders (`biometric_data/`, `demographic_data/`, `enrolment_data/`) are pushed to GitHub

2. **Large Files**: If data files are too large for GitHub:
   - Use Git LFS (Large File Storage)
   - Or upload to cloud storage and load from URL

3. **Environment Variables**: If you need to hide sensitive data, use Render environment variables

4. **Custom Domain**: 
   - Render: Settings → Custom Domain → Add your domain
   - Netlify/Vercel: Similar process in settings

### 🎯 Quick Start (After Deployment)

Your API will be available at:
```
https://your-api.onrender.com/api/overview
https://your-api.onrender.com/api/states
https://your-api.onrender.com/api/monthly
```

Your frontend will be at:
```
https://your-site.netlify.app
```

### 💰 Costs

- **Backend (Render Free)**: $0/month
  - 750 hours/month free tier
  - Spins down after inactivity
  
- **Frontend (Netlify Free)**: $0/month
  - 100 GB bandwidth
  - Unlimited deploys

**Total: FREE! 🎉**

### 🆙 Upgrade Options

If you need better performance:
- Render Starter: $7/month (always-on, more resources)
- Netlify Pro: $19/month (more bandwidth)

---

## Local Development

To run locally:

```bash
# Backend
cd backend
pip install -r requirements.txt
python app_api.py
# Runs at http://localhost:5000

# Frontend
# Just open frontend/index.html in browser
# Or use Live Server in VS Code
```

## Support

For issues:
1. Check Render logs
2. Test API endpoints directly
3. Check browser console
4. Verify data files are present

---

Made with ❤️ for Aadhaar Youth Biometric Analysis
