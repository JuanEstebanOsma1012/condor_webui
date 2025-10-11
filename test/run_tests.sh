#!/bin/bash

# HTCondor Web UI Test Runner
# This script helps run the automated test suite with proper setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}HTCondor Web UI Test Runner${NC}"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"

# Install dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -q -r "$SCRIPT_DIR/test_requirements.txt"

# Check if ChromeDriver is available
if ! command -v chromedriver &> /dev/null; then
    echo -e "${RED}Warning: ChromeDriver not found in PATH${NC}"
    echo "Please install ChromeDriver:"
    echo "  sudo apt-get install chromium-chromedriver"
    echo "Or download from: https://chromedriver.chromium.org/"
fi

# Change to test directory
cd "$SCRIPT_DIR"

# Parse command line arguments
HEADLESS=""
TEST_SPECIFIC=""
TEST_URL="http://172.30.27.11:5000"

while [[ $# -gt 0 ]]; do
    case $1 in
        --headless)
            HEADLESS="--headless"
            shift
            ;;
        --test)
            TEST_SPECIFIC="--test $2"
            shift 2
            ;;
        --url)
            TEST_URL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --headless       Run tests in headless mode"
            echo "  --test TEST_ID   Run specific test (ESC-01, ESC-02, ESC-03)"
            echo "  --url URL        Specify application URL (default: http://172.30.27.11:5000)"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Run all tests"
            echo "  $0 --headless               # Run all tests in headless mode"
            echo "  $0 --test ESC-01             # Run only ESC-01"
            echo "  $0 --test ESC-02 --headless  # Run ESC-02 in headless mode"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Run tests
echo -e "${BLUE}Starting automated tests...${NC}"
echo "Test configuration:"
echo "  URL: $TEST_URL"
echo "  Headless: $([ -n "$HEADLESS" ] && echo "Yes" || echo "No")"
echo "  Specific test: $([ -n "$TEST_SPECIFIC" ] && echo "${TEST_SPECIFIC#--test }" || echo "All tests")"
echo ""

# Execute the test suite
python automated_test_suite.py --url "$TEST_URL" $HEADLESS $TEST_SPECIFIC

TEST_EXIT_CODE=$?

# Display results
echo ""
echo "=================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests completed successfully!${NC}"
else
    echo -e "${RED}✗ Some tests failed or encountered errors${NC}"
fi

# Show report location
if [ -f "test_report.json" ]; then
    echo -e "${BLUE}Detailed report available at: $(pwd)/test_report.json${NC}"
fi

if [ -f "test_results.log" ]; then
    echo -e "${BLUE}Execution log available at: $(pwd)/test_results.log${NC}"
fi

# Cleanup
if [ -n "$APP_PID" ]; then
    echo ""
    echo "Stopping background Flask application (PID: $APP_PID)..."
    kill $APP_PID 2>/dev/null || true
fi

deactivate

echo ""
echo "Test execution completed."
exit $TEST_EXIT_CODE
