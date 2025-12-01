#!/bin/bash

# Function to cleanup processes on exit
cleanup() {
    echo "Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID
    fi
}

trap cleanup EXIT

# Kill any existing processes on ports
fuser -k 8000/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null

# Start Backend
echo "Starting Backend (TESTING mode)..."
cd ../backend
export TESTING=True
# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found!"
    exit 1
fi

# Initialize Database
echo "Initializing Database..."
python3 -c "from app.database import init_db; init_db()"

uvicorn app.main:app --port 8000 > ../auto_tests/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "Waiting for Backend..."
sleep 5
# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Backend failed to start. Check backend.log"
    cat backend.log
    exit 1
fi

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm run dev -- --port 5173 > ../auto_tests/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
echo "Waiting for Frontend..."
sleep 5

# Run Cypress
echo "Running Cypress Tests..."
cd frontend
npx cypress run
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Tests passed successfully!"
else
    echo "❌ Tests failed!"
fi

exit $EXIT_CODE
