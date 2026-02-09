/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost';
    // Ensure URL has protocol
    const destination = apiUrl.startsWith('http') 
      ? `${apiUrl}/api/:path*`
      : `https://${apiUrl}/api/:path*`;
    
    return [
      {
        source: '/api/:path*',
        destination,
      },
    ]
  },
}

export default nextConfig
