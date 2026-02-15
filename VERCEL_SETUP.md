# Vercel Environment Variable Setup

## The Problem
Your frontend is trying to call the backend API, but it doesn't know where the backend is located. This causes the "Error loading dashboard" message.

## The Solution
Set the `NEXT_PUBLIC_API_URL` environment variable in Vercel.

## Step-by-Step Instructions

### 1. Go to Vercel Dashboard
- Visit https://vercel.com/dashboard
- Select your `dientex` project

### 2. Navigate to Settings
- Click on the "Settings" tab at the top
- Click on "Environment Variables" in the left sidebar

### 3. Add the Environment Variable
Click "Add New" and enter:

```
Key:   NEXT_PUBLIC_API_URL
Value: https://api.dientex.com
```

**Important:** Make sure to check all three environments:
- ✅ Production
- ✅ Preview  
- ✅ Development

### 4. Redeploy
After adding the variable, you MUST redeploy:

**Option A: Trigger a new deployment**
- Go to the "Deployments" tab
- Click the three dots (⋯) on the latest deployment
- Click "Redeploy"
- Confirm the redeployment

**Option B: Push a new commit**
- Make any small change to your code
- Push to GitHub
- Vercel will automatically deploy

### 5. Verify
Once redeployed, visit https://dientex.com and the dashboard should load with data.

## How to Verify It's Working

### Check in Browser Console:
1. Open https://dientex.com
2. Press F12 to open Developer Tools
3. Go to "Network" tab
4. Refresh the page
5. Look for a request to `/api/dashboard/`
6. It should show: `https://api.dientex.com/api/dashboard/`
7. Status should be `200 OK`

### Check with curl:
```bash
# Test backend directly
curl https://api.dientex.com/api/dashboard/

# Should return JSON like:
# {"today":{"appointments":0,"patients_attended":0,"income":0.0},...}
```

## Troubleshooting

### Still seeing "Error loading dashboard"?
1. Verify the environment variable is set correctly (no typos)
2. Make sure you redeployed after adding the variable
3. Check that your Railway backend is running
4. Test the backend URL directly: https://api.dientex.com/api/dashboard/

### Getting CORS errors?
Check your Railway environment variables:
- `DOMAIN` should be set to `dientex.com`
- Backend logs should show: `ALLOWED_HOSTS: ['dientex.com', 'api.dientex.com', 'www.dientex.com']`

### Backend not responding?
1. Check Railway deployment logs
2. Verify database is connected
3. Test health endpoint: https://api.dientex.com/health/

## What Changed in the Code

I made these changes to fix the issue:

1. **Backend URLs** (`backend/_config/urls.py`):
   - Changed `/dashboard/` → `/api/dashboard/`
   - Changed all app URLs to use `/api/` prefix

2. **Frontend Config** (`frontend/next.config.ts`):
   - Already configured to rewrite `/api/*` to backend
   - Uses `NEXT_PUBLIC_API_URL` environment variable

3. **Package.json** (`frontend/package.json`):
   - Removed `engines.node` to eliminate Vercel warning

## Summary

The fix is simple:
1. ✅ Code changes are done (backend URLs now use `/api/` prefix)
2. ⏳ Set `NEXT_PUBLIC_API_URL=https://api.dientex.com` in Vercel
3. ⏳ Redeploy frontend
4. ✅ Dashboard should work!
