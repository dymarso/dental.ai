# Fix Vercel Root Directory Configuration

## The Problem

Vercel is trying to build from the repository root, but your Next.js app is in the `frontend` directory.

Error: `cd: frontend: No such file or directory`

## The Solution

Configure Vercel to use `frontend` as the root directory.

## Step-by-Step Fix

### Option 1: Via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Select your `dientex` project
3. Click "Settings"
4. Scroll down to "Root Directory"
5. Click "Edit"
6. Enter: `frontend`
7. Click "Save"
8. Go to "Deployments" and redeploy

### Option 2: Via vercel.json (Alternative)

If you prefer to keep it in code, update `vercel.json`:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs",
  "buildCommand": "cd frontend && npm run build",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "outputDirectory": "frontend/.next"
}
```

But Option 1 is cleaner and recommended.

## After Fixing

Once you set the root directory:

1. Redeploy from Vercel dashboard
2. Build should complete successfully
3. Then set the environment variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://api.dientex.com`
4. Redeploy again
5. Dashboard should work!

## Quick Verification

After deployment:
```bash
# Test backend
curl https://api.dientex.com/api/dashboard/

# Visit frontend
open https://dientex.com
```

## Summary

1. ✅ Set Root Directory to `frontend` in Vercel Settings
2. ✅ Redeploy
3. ✅ Set `NEXT_PUBLIC_API_URL` environment variable
4. ✅ Redeploy again
5. ✅ Done!
