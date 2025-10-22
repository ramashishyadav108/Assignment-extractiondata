#!/bin/bash
# Test the backend health endpoint

echo "Testing backend health..."
echo ""

# Check if backend is running
response=$(curl -s http://localhost:8000/health)

if [ $? -eq 0 ]; then
    echo "✓ Backend is running!"
    echo "Response: $response"
else
    echo "✗ Backend is not running or not accessible"
    echo ""
    echo "To start the backend:"
    echo "  cd backend"
    echo "  ./start.sh"
fi
