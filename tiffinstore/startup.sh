#!/bin/bash
set -e

echo "📦 1. Installing Python dependencies..."
pip install -q -r product-service/requirements.txt
pip install -q -r payment-service/requirements.txt
pip install -q -r shipping-service/requirements.txt

echo "📦 2. Installing Node.js dependencies..."
(cd user-service && npm install --silent)
(cd cart-service && npm install --silent)

echo "🚀 3. Starting Backend Microservices in background..."
(cd product-service && uvicorn app:app --host 127.0.0.1 --port 5001 &)
(cd user-service && node server.js &)
(cd cart-service && node server.js &)
(cd payment-service && uvicorn app:app --host 127.0.0.1 --port 5004 &)
(cd shipping-service && uvicorn app:app --host 127.0.0.1 --port 5005 &)

echo "🌐 4. Configuring and starting Nginx on Port 8080..."
sudo apt-get update -qq && sudo apt-get install -y -qq nginx
# Update root path dynamically to match current Codespace directory
sed "s|/usr/share/nginx/html|$(pwd)/frontend|g; s|product-service|127.0.0.1|g; s|user-service|127.0.0.1|g; s|cart-service|127.0.0.1|g; s|payment-service|127.0.0.1|g; s|shipping-service|127.0.0.1|g" frontend/nginx.conf | sudo tee /etc/nginx/conf.d/tiffinstore.conf > /dev/null
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -s reload || sudo nginx

echo "✅ All TiffinStore services are running! Open Port 8080 in the Codespaces 'Ports' tab."