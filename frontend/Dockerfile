# Use Node.js for building
FROM node:18-slim

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the code
COPY . .

# Start the development server
EXPOSE 3000
CMD ["npm", "start"]
