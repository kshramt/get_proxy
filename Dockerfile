FROM node:20.3.0-bullseye as base_js
ENV PLAYWRIGHT_BROWSERS_PATH /ms-playwright
RUN mkdir -p "${PLAYWRIGHT_BROWSERS_PATH}"
WORKDIR /app
COPY --link package.json package-lock.json ./

FROM base_js as builder_js
RUN --mount=type=cache,target=/root/.npm --mount=type=cache,target=/root/.cache npm ci
COPY --link tsconfig.json tsconfig.json
COPY --link src src
RUN npm run build

FROM base_js as prod_api
RUN --mount=type=cache,target=/root/.npm --mount=type=cache,target=/root/.cache npm ci --omit=dev
RUN --mount=type=cache,target=/ms-playwright npx playwright install --with-deps chromium \
   && rm -rf /var/lib/apt/lists/*
COPY --link --from=builder_js /app/dist dist

FROM prod_api as test_api
RUN --mount=type=cache,target=/root/.npm --mount=type=cache,target=/root/.cache npm ci
COPY --link tsconfig.json tsconfig.json
COPY --link src src
COPY --link scripts/check.sh scripts/check.sh

FROM prod_api as prod
RUN rm -rf package.json package-lock.json
RUN adduser --disabled-password --gecos '' app
USER app

EXPOSE 8080
ENTRYPOINT ["node", "dist/index.js"]
