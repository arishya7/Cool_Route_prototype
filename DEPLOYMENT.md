# CoolRide Deployment Guide - Render (Free Tier)

## Overview
This guide will help you deploy CoolRide to Render for **FREE**. Your app will be split into:
- **Backend API** (simple_server.py) - Web Service
- **Frontend** (index.html) - Static Site

## Prerequisites
1. GitHub account
2. Render account (sign up at https://render.com - free!)
3. Your code pushed to a GitHub repository

## Step-by-Step Deployment

### 1. Push Code to GitHub

First, make sure all your code is committed and pushed to GitHub:

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Render

#### Option A: Deploy using Blueprint (Recommended - Easiest!)

1. Go to https://render.com/
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create both services
5. Click "Apply" to deploy!

#### Option B: Manual Deployment

**Deploy Backend:**
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Settings:
   - **Name:** coolride-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python simple_server.py`
   - **Plan:** Free
5. Click "Create Web Service"

**Deploy Frontend:**
1. Click "New +" → "Static Site"
2. Connect same GitHub repo
3. Settings:
   - **Name:** coolride-frontend
   - **Build Command:** (leave empty)
   - **Publish Directory:** `.` (current directory)
   - **Plan:** Free
4. Click "Create Static Site"

### 3. Configure URLs

After deployment, you'll get two URLs:
- Backend: `https://coolride-api.onrender.com`
- Frontend: `https://coolride-frontend.onrender.com`

The frontend is already configured to auto-detect the backend URL!

### 4. Test Your Deployment

1. Visit your frontend URL: `https://coolride-frontend.onrender.com`
2. Try calculating a route from "Tampines MRT" to "Tampines Eco Green"
3. First request may take 30-60 seconds (free tier cold start)

## Important Notes

### Free Tier Limitations
- ✅ 750 free hours/month (plenty for testing)
- ⚠️ Services sleep after 15 minutes of inactivity
- ⏱️ First request after sleep: 30-60 second wake-up time
- ✅ Automatic HTTPS
- ✅ Continuous deployment from GitHub

### Data Files
Your data files (`data/` folder and `trees_downloaded.csv`) will automatically be included:
- Total size: ~62MB (well under GitHub's 100MB file limit)
- Files are cloned during deployment and available to your Python code
- No special configuration needed!

### Environment Variables
If you need to add secrets (like API keys), go to:
- Render Dashboard → Your Service → Environment
- Add variables there (never commit secrets to Git!)

## Troubleshooting

### "Service Unavailable" Error
- **Cause:** Service is sleeping (free tier)
- **Solution:** Wait 30-60 seconds for it to wake up

### Build Fails
- Check Render logs in the dashboard
- Common issue: Missing dependencies in `requirements.txt`

### Frontend Can't Connect to Backend
- Check the API URL in the browser console
- Verify backend service is running in Render dashboard
- Check CORS settings in `simple_server.py`

### Route Calculation Fails
- Ensure all data files were pushed to GitHub
- Check backend logs for errors
- Verify OSM API is accessible

## Updating Your Deployment

Every time you push to GitHub, Render automatically redeploys:

```bash
git add .
git commit -m "Update feature X"
git push
```

Render will rebuild and redeploy automatically!

## Cost Optimization

To stay within free tier limits:
- App sleeps when not in use (automatic)
- Use efficient queries in your code
- Monitor usage in Render dashboard

## Alternative: Keep Service Awake (Hack)

Use a free uptime monitor like UptimeRobot to ping your service every 5 minutes:
1. Sign up at https://uptimerobot.com (free)
2. Create monitor for: `https://coolride-api.onrender.com`
3. Set interval: 5 minutes

**Note:** This uses more of your 750 free hours but keeps the service responsive.

## Next Steps

- Add custom domain (available on paid tiers)
- Upgrade to paid tier for no sleep ($7/month)
- Add analytics/monitoring
- Set up staging environment

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: Create issues in your repo

---

**Deployment Status Checklist:**
- [ ] Code pushed to GitHub
- [ ] Backend deployed on Render
- [ ] Frontend deployed on Render
- [ ] Frontend can connect to backend
- [ ] Test route calculation works
- [ ] Monitor first 24 hours for issues

Good luck with your deployment! 🚀
