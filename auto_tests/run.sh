# Fichier pour lancer automatiquement tous les tests
# Il démarre le backend et le frontend, exécute les tests Bruno, Pytest et Cypress.

cd "$(dirname "$0")"

# Function to cleanup processes on exit
cleanup() {
    echo "Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    fuser -k 8000/tcp 2>/dev/null
    fuser -k 5173/tcp 2>/dev/null
}

trap cleanup EXIT

# Kill any existing processes on ports
fuser -k 8000/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null

# Start Backend
echo "Starting Backend (TESTING mode)..."
cd ../backend
export TESTING=True
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test_secret_key_for_pipeline"

# Remove existing database to ensure clean state
if [ -f "test.db" ]; then
    rm test.db
    echo "Removed existing test database."
fi

# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found! Please run 'python3 -m venv venv' in backend folder."
    exit 1
fi

# Initialize Database
echo "Initializing Database..."
python3 -c "from app.database import init_db_test; init_db_test()"

uvicorn app.main:app --port 8000 > ../auto_tests/backend.log 2>&1 &
BACKEND_PID=$!
cd ../auto_tests

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
cd ../frontend
npm run dev -- --port 5173 > ../auto_tests/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../auto_tests

# Wait for frontend to be ready
echo "Waiting for Frontend..."
sleep 5

# Track failures
FAILED=0

# --- 1. Run Bruno Tests ---
echo "------------------------------------------------"
echo "Running Bruno API Tests..."

target_dir="../backend/bruno"

if [ -d "$target_dir" ]; then
    current_dir=$(pwd)
    cd "$target_dir"
    echo "Executing Bruno in $(pwd)..."
    npx @usebruno/cli run . --env "local"
    BRUNO_EXIT=$?
    cd "$current_dir"
else
    echo "⚠️  Bruno test directory not found at $target_dir"
    BRUNO_EXIT=1
fi

if [ $BRUNO_EXIT -eq 0 ]; then
    echo "✅ Bruno Tests passed!"
else
    echo "❌ Bruno Tests failed!"
    FAILED=1
fi

# --- 2. Run Pytest ---
echo "------------------------------------------------"
echo "Running Pytest Tests..."
cd ../backend
export SECRET_KEY="test_secret_key_for_pipeline" 
pytest
PYTEST_EXIT=$?
cd ../auto_tests

if [ $PYTEST_EXIT -eq 0 ]; then
    echo "✅ Backend Tests passed!"
else
    echo "❌ Backend Tests failed!"
    FAILED=1
fi

# --- 3. Run Cypress ---
echo "------------------------------------------------"
echo "Running Cypress Tests..."
cd ../frontend
npx cypress install
npx cypress run #--spec "cypress/e2e/navigation.cy.js"
CYPRESS_EXIT=$?
cd ../auto_tests

if [ $CYPRESS_EXIT -eq 0 ]; then
    echo "✅ Frontend Tests passed!"
else
    echo "❌ Frontend Tests failed!"
    FAILED=1
fi

echo "------------------------------------------------"
if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉"
    exit 0
else
    echo "🔥 SOME TESTS FAILED! Check logs above. 🔥"
    exit 1
fi
