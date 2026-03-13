# 🚀 Vercel Backend Deployment Guide

Deploy your GDP Growth Prediction backend API on Vercel.

---

## ⚡ Quick Deploy (5 minutes)

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Click **"Add New"** → **"Project"**

2. **Import Repository**
   - Click **"Import Git Repository"**
   - Paste: `https://github.com/jay192005/vikal.ai-backend.git`
   - Click **"Import"**

3. **Configure Project**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Add Environment Variables**
   
   Click **"Environment Variables"** and add these 4 variables:

   **FIREBASE_CREDENTIALS** (Required)
   ```
   {"type":"service_account","project_id":"gdp-grow-prediction-model",...}
   ```
   (Single-line JSON from your firebase_credentials.json file)

   **PORT** (Optional)
   ```
   5000
   ```

   **FLASK_ENV** (Optional)
   ```
   production
   ```

   **CORS_ORIGINS** (Required - update after frontend deployment)
   ```
   https://your-frontend.vercel.app
   ```

   **Important**: Select all environments (Production, Preview, Development)

5. **Deploy**
   - Click **"Deploy"**
   - Wait 3-5 minutes for build
   - Your API will be live at: `https://your-backend.vercel.app`

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Clone repository
git clone https://github.com/jay192005/vikal.ai-backend.git
cd vikal.ai-backend

# Deploy
vercel

# Deploy to production
vercel --prod
```

---

## 📋 Environment Variables Required

You need to set these environment variables in Vercel:

| Variable | Required | Description |
|----------|----------|-------------|
| `FIREBASE_CREDENTIALS` | ✅ Yes | Firebase Admin SDK credentials (single-line JSON) |
| `PORT` | ❌ No | Port number (default: 5000) |
| `FLASK_ENV` | ❌ No | Flask environment (default: production) |
| `CORS_ORIGINS` | ✅ Yes | Allowed frontend URLs (comma-separated) |

### How to Get FIREBASE_CREDENTIALS

Convert your `firebase_credentials.json` to a single line:

**Windows (PowerShell):**
```powershell
python -c "import json; print(json.dumps(json.load(open('firebase_credentials.json'))))"
```

**Linux/Mac:**
```bash
python3 -c "import json; print(json.dumps(json.load(open('firebase_credentials.json'))))"
```

Copy the entire output and paste it as the value for `FIREBASE_CREDENTIALS`.

---

## 🔧 Configuration Files

This repository includes:

- ✅ `vercel.json` - Vercel configuration for Python
- ✅ `api/index.py` - Serverless function entry point
- ✅ `.vercelignore` - Files to exclude from deployment
- ✅ `requirements.txt` - Python dependencies
- ✅ `app_scenario.py` - Main Flask application

---

## 🧪 Test Locally Before Deploying

```bash
# Clone repository
git clone https://github.com/jay192005/vikal.ai-backend.git
cd vikal.ai-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable (for testing)
# On Windows PowerShell:
$env:FIREBASE_CREDENTIALS='{"type":"service_account",...}'

# On Linux/Mac:
export FIREBASE_CREDENTIALS='{"type":"service_account",...}'

# Run locally
python app_scenario.py

# Test at http://localhost:5000
```

---

## ✅ Verify Deployment

After deployment, test your API:

### Test Root Endpoint
```bash
curl https://your-backend.vercel.app/
```

Expected response:
```json
{
  "name": "Vikalp.ai - GDP Economic Scenario Simulator",
  "version": "v4.0-scenario",
  "model_loaded": true,
  "endpoints": {...}
}
```

### Test Countries Endpoint
```bash
curl https://your-backend.vercel.app/api/countries
```

Expected: Array of 203 countries

### Test Simulation
```bash
curl -X POST https://your-backend.vercel.app/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "Country": "United States",
    "Population_Growth_Rate": 1.0,
    "Exports_Growth_Rate": 10.0,
    "Imports_Growth_Rate": 5.0,
    "Investment_Growth_Rate": 8.0,
    "Consumption_Growth_Rate": 3.0,
    "Govt_Spend_Growth_Rate": 2.0
  }'
```

Expected: Prediction result with GDP growth rate

---

## 🔄 Update Frontend with Backend URL

After backend is deployed:

1. Copy your backend URL: `https://your-backend.vercel.app`
2. Go to frontend project in Vercel
3. **Settings → Environment Variables**
4. Update `VITE_API_BASE_URL` with your backend URL
5. Redeploy frontend

---

## 🔄 Update Backend CORS

After frontend is deployed:

1. Copy your frontend URL: `https://your-frontend.vercel.app`
2. Go to backend project in Vercel
3. **Settings → Environment Variables**
4. Update `CORS_ORIGINS` with your frontend URL
5. Redeploy backend

Or update `app_scenario.py` and push to GitHub:

```python
allowed_origins = [
    "http://localhost:5173",  # Local dev
    "https://your-frontend.vercel.app",  # Production
]
```

---

## 🆘 Troubleshooting

### "Module not found"
**Solution**: 
- Check `requirements.txt` includes all dependencies
- Redeploy after updating

### "Model files not found"
**Solution**:
- Ensure `.pkl` files are in repository
- Check `.vercelignore` doesn't exclude them
- Verify files are committed to git

### "Firebase initialization failed"
**Solution**:
- Check `FIREBASE_CREDENTIALS` is set correctly
- Ensure it's valid single-line JSON
- Test locally first

### "Function timeout"
**Solution**:
- Vercel free tier: 10-second timeout
- Upgrade to Pro for 60-second timeout
- Or optimize model loading

### "CORS error"
**Solution**:
- Update `CORS_ORIGINS` in Vercel
- Include your frontend URL
- Redeploy backend

---

## 📊 API Endpoints

### GET /
Returns API information and status

### GET /api/countries
Returns list of 203 countries

### GET /api/history?country=United%20States
Returns historical GDP data for a country

### POST /simulate
Simulates economic scenario and returns predicted GDP growth

**Request Body:**
```json
{
  "Country": "United States",
  "Population_Growth_Rate": 1.0,
  "Exports_Growth_Rate": 10.0,
  "Imports_Growth_Rate": 5.0,
  "Investment_Growth_Rate": 8.0,
  "Consumption_Growth_Rate": 3.0,
  "Govt_Spend_Growth_Rate": 2.0
}
```

### GET /api/baseline?country=United%20States
Returns baseline (average) growth rates for a country

---

## 🔒 Security

### Best Practices

- ✅ Use environment variables for secrets
- ✅ Never commit `firebase_credentials.json`
- ✅ Use HTTPS only (Vercel provides automatically)
- ✅ Configure CORS properly
- ✅ Validate all inputs
- ✅ Use Firebase Admin SDK for authentication

---

## 📈 Performance

### Vercel Limits (Free Tier)

- **Function Timeout**: 10 seconds
- **Function Size**: 50 MB
- **Bandwidth**: 100 GB/month
- **Invocations**: Unlimited

### Your Project

- **Model Size**: ~16 MB ✅ (within limits)
- **Prediction Time**: ~1-2 seconds ✅ (within timeout)
- **Cold Start**: ~1-2 seconds ✅ (fast)

---

## 💡 Pro Tips

### 1. Monitor Logs

View real-time logs in Vercel:
1. Go to project dashboard
2. Click **"Deployments"**
3. Click on latest deployment
4. Click **"Functions"** tab
5. View logs for each request

### 2. Preview Deployments

Every push creates a preview:
- Test before merging to main
- Share preview URL with team
- Automatic for every PR

### 3. Custom Domain

Add custom domain:
1. Go to **Project Settings → Domains**
2. Add your domain
3. Update DNS records
4. Vercel handles SSL automatically

### 4. Automatic Deployments

Connect to GitHub:
1. Go to **Project Settings → Git**
2. Connect repository
3. Every push to `main` auto-deploys

---

## 📝 Quick Commands Reference

### Deploy
```bash
vercel --prod
```

### View Logs
```bash
vercel logs your-backend.vercel.app
```

### List Deployments
```bash
vercel ls
```

### Environment Variables
```bash
# List
vercel env ls

# Add
vercel env add FIREBASE_CREDENTIALS

# Remove
vercel env rm FIREBASE_CREDENTIALS
```

---

## 🎯 Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] `vercel.json` configured
- [ ] `api/index.py` created
- [ ] `.vercelignore` configured
- [ ] `requirements.txt` updated
- [ ] Model files (.pkl) in repository
- [ ] Data file (.csv) in repository
- [ ] Firebase credentials converted to single line
- [ ] Deploy to Vercel
- [ ] Add environment variables
- [ ] Test API endpoints
- [ ] Copy backend URL
- [ ] Update frontend with backend URL
- [ ] Update backend CORS with frontend URL
- [ ] Redeploy both
- [ ] Test end-to-end

---

## 🌐 Your Deployed API

After deployment:

- **Backend URL**: `https://your-backend.vercel.app`
- **API Docs**: `https://your-backend.vercel.app/`
- **Countries**: `https://your-backend.vercel.app/api/countries`
- **Simulate**: `https://your-backend.vercel.app/simulate`

---

## 📚 Additional Resources

- **Vercel Docs**: https://vercel.com/docs
- **Python on Vercel**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **Flask Documentation**: https://flask.palletsprojects.com/

---

## 🎉 Success!

Your backend API is deployed and ready to serve predictions!

**Next Steps**:
1. Test all endpoints
2. Update frontend with backend URL
3. Update backend CORS with frontend URL
4. Monitor logs and performance
5. Share API with users

