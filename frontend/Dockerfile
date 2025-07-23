# Dockerfile for Next.js Frontend (Production) - UPDATED
FROM node:18-alpine

# Install tools needed for health checks
RUN apk add --no-cache wget curl

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./
COPY package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# UPDATED: Health check with better error handling and longer startup time
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || \
        curl -f http://localhost:3000/api/health || \
        curl -f http://localhost:3000/ || \
        wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the application
CMD ["npm", "start"]