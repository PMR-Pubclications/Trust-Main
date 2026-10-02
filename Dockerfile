FROM node:18-alpine

# Create app directory
WORKDIR /app

# Set environment
ENV NODE_ENV=production

# Install dependencies
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci --only=production; else npm install --production; fi

# Copy application files
COPY . .

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', res=>{if(res.statusCode===200) process.exit(0); else process.exit(1)}).on('error', ()=>process.exit(1))"

CMD ["node", "server.js"]

FROM node:20-bookworm-slim

# Create app directory
WORKDIR /app

# Install dumb-init for proper signal handling
RUN apt-get update && apt-get install -y --no-install-recommends dumb-init ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Copy package manifests first for better layer caching
COPY package*.json ./

# Install production deps (fallback to npm install if lockfile missing)
RUN if [ -f package-lock.json ]; then npm ci --omit=dev; else npm install --omit=dev; fi

# Copy app source
COPY . .

# Set runtime env
ENV NODE_ENV=production
ENV PORT=3000

# Non-root user
RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

# Optional healthcheck (assumes app responds on /health)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:' + (process.env.PORT||3000) + '/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

ENTRYPOINT ["dumb-init", "--"]

# Adjust if your start command differs
CMD ["npm", "start"]
