/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    
    // Only add rewrite if API URL is configured
    if (!apiUrl) {
      console.warn('NEXT_PUBLIC_API_URL not set, API calls will fail');
      return [];
    }
    
    // Ensure URL has protocol
    const destination = apiUrl.startsWith('http') 
      ? `${apiUrl}/:path*`
      : `https://${apiUrl}/:path*`;
    
    console.log('API rewrite configured:', { source: '/api/:path*', destination });
    
    return [
      {
        source: '/api/:path*',
        destination,
      },
    ]
  },
}

export default nextConfig
