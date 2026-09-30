# security/Dockerfile
#
# Production image for the standalone Trust security service
# (voice-token telemetry endpoint + health/status). See security/README.md
# for what is and is not included in this image.
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=production

# Install dependencies first for better layer caching
COPY security/package.json security/package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci --omit=dev; else npm install --omit=dev; fi

# Copy only the security service source
COPY security/server.js ./server.js
COPY security/voice ./voice
COPY security/nfc ./nfc
COPY security/auth ./auth

# Non-root execution
RUN addgroup -S security && adduser -S security -G security \
    && chown -R security:security /app
USER security

EXPOSE 3100

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://127.0.0.1:' + (process.env.SECURITY_PORT || 3100) + '/health', res => { if (res.statusCode === 200) process.exit(0); else process.exit(1); }).on('error', () => process.exit(1))"

CMD ["node", "server.js"]
