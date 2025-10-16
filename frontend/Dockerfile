FROM node:18-alpine

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm ci

# Copy the rest of the application
COPY . ./

# Expose port 3000
EXPOSE 3000

# Start development server by default
CMD ["npm", "run", "dev"]