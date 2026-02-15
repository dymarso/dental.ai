#!/bin/bash

# Deployment Verification Script
# This script tests if your backend and frontend are properly configured

echo "🔍 Verifying Dientex Deployment..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL="https://api.dientex.com"
FRONTEND_URL="https://dientex.com"

# Test 1: Backend Health Check
echo "1️⃣  Testing backend health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BACKEND_URL}/health/")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
else
    echo -e "${RED}❌ Backend health check failed (HTTP $HEALTH_RESPONSE)${NC}"
    echo "   Make sure your Railway backend is running"
fi
echo ""

# Test 2: Dashboard API Endpoint
echo "2️⃣  Testing dashboard API endpoint..."
DASHBOARD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BACKEND_URL}/api/dashboard/")
if [ "$DASHBOARD_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Dashboard API endpoint accessible${NC}"
    echo "   Response preview:"
    curl -s "${BACKEND_URL}/api/dashboard/" | head -c 200
    echo "..."
else
    echo -e "${RED}❌ Dashboard API endpoint failed (HTTP $DASHBOARD_RESPONSE)${NC}"
    echo "   Expected: ${BACKEND_URL}/api/dashboard/"
fi
echo ""
echo ""

# Test 3: Frontend Accessibility
echo "3️⃣  Testing frontend accessibility..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}")
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${RED}❌ Frontend not accessible (HTTP $FRONTEND_RESPONSE)${NC}"
fi
echo ""

# Test 4: CORS Configuration
echo "4️⃣  Testing CORS configuration..."
CORS_RESPONSE=$(curl -s -H "Origin: ${FRONTEND_URL}" -H "Access-Control-Request-Method: GET" -X OPTIONS "${BACKEND_URL}/api/dashboard/" -o /dev/null -w "%{http_code}")
if [ "$CORS_RESPONSE" = "200" ] || [ "$CORS_RESPONSE" = "204" ]; then
    echo -e "${GREEN}✅ CORS appears to be configured${NC}"
else
    echo -e "${YELLOW}⚠️  CORS preflight returned HTTP $CORS_RESPONSE${NC}"
    echo "   This might be okay if your backend doesn't require preflight"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. If backend tests failed, check Railway deployment logs"
echo "2. If dashboard API failed, verify URL changes were deployed"
echo "3. In Vercel, set environment variable:"
echo "   NEXT_PUBLIC_API_URL=${BACKEND_URL}"
echo "4. Redeploy frontend in Vercel after setting the variable"
echo ""
echo "To test locally:"
echo "  Backend:  cd backend && python manage.py runserver"
echo "  Frontend: cd frontend && npm run dev"
echo ""
