/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  serverExternalPackages: ["@prisma/client", "prisma"],
  trailingSlash: true,
  
  // Critical fixes for React import issues
  experimental: {
    esmExternals: true,
    optimizeCss: false,
  },
  
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Fix React import issues
    config.resolve.alias = {
      ...config.resolve.alias,
      'react': 'react',
      'react-dom': 'react-dom',
    }
    
    // Ensure React is available globally
    config.plugins.push(
      new webpack.ProvidePlugin({
        React: 'react',
      })
    )
    
    // Fix module resolution that causes TDZ
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
      crypto: false,
      stream: false,
      url: false,
      zlib: false,
      http: false,
      https: false,
      assert: false,
      os: false,
      path: false,
    }
    
    // Handle circular dependencies and TDZ issues
    if (!dev && !isServer) {
      // Custom chunk splitting to avoid TDZ errors
      config.optimization.splitChunks = {
        chunks: 'all',
        minSize: 20000,
        maxSize: 244000,
        cacheGroups: {
          // React vendor chunk
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            name: 'react-vendor',
            chunks: 'all',
            priority: 30,
            reuseExistingChunk: true,
          },
          // Other vendor chunks
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 20,
            reuseExistingChunk: true,
          },
          // Common chunks
          commons: {
            name: 'commons',
            minChunks: 2,
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true,
          },
          // UI components
          ui: {
            test: /[\\/]components[\\/]ui[\\/]/,
            name: 'ui',
            chunks: 'all',
            priority: 15,
            reuseExistingChunk: true,
          },
          // Default chunk
          default: {
            minChunks: 2,
            priority: 5,
            reuseExistingChunk: true,
          },
        },
      }
      
      // Prevent problematic optimizations that cause TDZ
      config.optimization = {
        ...config.optimization,
        providedExports: false,
        usedExports: false,
        sideEffects: false,
        innerGraph: false,
        realContentHash: false,
        minimize: true,
      }
    }
    
    return config
  },
  
  // Disable problematic optimizations during build
  reactStrictMode: false, // Temporarily disable to avoid double rendering
  
  // Production optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // Enable gzip compression
  compress: true,
  
  // PoweredBy header
  poweredByHeader: false,
  
  // Generate ETags for caching
  generateEtags: true,
}

export default nextConfig