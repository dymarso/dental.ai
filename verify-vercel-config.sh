#!/bin/bash

echo "🔍 Verifying Vercel Configuration for Dientex"
echo "=============================================="
echo ""

echo "✅ vercel.json configuration:"
cat vercel.json | grep -A 5 "rewrites"
echo ""

echo "📋 Required Vercel Project Settings:"
echo "  - Root Directory: frontend"
echo "  - Build Command: npm run build (or default)"
echo "  - Output Directory: .next (or default)"
echo ""

echo "🔑 Required Environment Variables:"
echo "  - NEXT_PUBLIC_API_URL=https://api.dientex.com"
echo ""

echo "🧪 Testing API endpoint:"
curl -s https://api.dientex.com/api/dashboard/ | head -c 100
echo ""
echo ""

echo "📝 Next Steps:"
echo "1. Go to Vercel Dashboard → Your Project → Settings"
echo "2. Set Root Directory to 'frontend'"
echo "3. Verify NEXT_PUBLIC_API_URL environment variable"
echo "4. Redeploy"
