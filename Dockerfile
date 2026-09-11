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
