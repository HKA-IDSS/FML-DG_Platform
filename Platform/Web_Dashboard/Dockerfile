# ---- Build Stage ----
FROM node:20 AS build

COPY . /dashboard

WORKDIR /dashboard

# Install dependencies
RUN npm install --force

# Build the app for production
RUN npm run build

# ---- Production Stage ----
FROM node:20-slim

WORKDIR /dashboard

# Install serve to serve the build directory
RUN npm install -g serve

# Copy built static files from build stage
COPY --from=build /dashboard/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]