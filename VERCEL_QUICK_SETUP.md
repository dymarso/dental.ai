# Vercel Quick Setup Guide

## Two Settings You Need to Configure

### 1️⃣ Root Directory

**Why:** Your Next.js app is in the `frontend` folder, not the repository root.

**How to fix:**
```
Vercel Dashboard → Your Project → Settings → Root Directory
Set to: frontend
Save
```

### 2️⃣ Environment Variable

**Why:** Frontend needs to know where your backend API is located.

**How to fix:**
```
Vercel Dashboard → Your Project → Settings → Environment Variables
Add New:
  Key: NEXT_PUBLIC_API_URL
  Value: https://api.dientex.com
  Environments: ✅ Production ✅ Preview ✅ Development
Save
```

### 3️⃣ Redeploy

After making both changes:
```
Vercel Dashboard → Deployments → Latest → ⋯ → Redeploy
```

## That's It!

Once redeployed, visit https://dientex.com and your dashboard should load with data.

## Visual Checklist

- [ ] Root Directory set to `frontend`
- [ ] Environment variable `NEXT_PUBLIC_API_URL` added
- [ ] Redeployed after changes
- [ ] Visited https://dientex.com to verify

## Test Commands

```bash
# Test backend is responding
curl https://api.dientex.com/api/dashboard/

# Should return JSON with dashboard data
```

## Troubleshooting

**Build fails with "No such file or directory"**
→ Root directory not set to `frontend`

**Dashboard shows "Error loading dashboard"**
→ Environment variable not set or not redeployed

**Getting CORS errors**
→ Check Railway has `DOMAIN=dientex.com` set

---

**Total time to fix: ~5 minutes**
