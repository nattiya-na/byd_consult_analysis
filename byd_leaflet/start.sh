#!/bin/bash
# Start BYD Leaflet — Flask backend + Vue frontend

echo "🚗 Starting BYD EV Recommender..."

# Backend
echo "→ Starting Flask API on :5050"
cd backend
python app.py &
FLASK_PID=$!
cd ..

# Give Flask a moment
sleep 1

# Frontend
echo "→ Starting Vue dev server on :5173"
cd frontend
npm run dev &
VITE_PID=$!
cd ..

echo ""
echo "✅ App running at: http://localhost:5173"
echo "   API running at: http://localhost:5050"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $FLASK_PID $VITE_PID 2>/dev/null; echo 'Stopped.'" INT
wait
