# Stage 1: Copy static assets into the container
FROM nginx:alpine

# Copy your static HTML and assets (like CSS, JS) into Nginx's default directory
COPY ./my-app/ /usr/share/nginx/html

# Expose port 80 to serve the content
EXPOSE 80

# Start Nginx to serve the files
CMD ["nginx", "-g", "daemon off;"]