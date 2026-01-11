#!/bin/bash

# Application configuration
APP_FILE="main.py"
PID_FILE=".app.pid"
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/app.log"
ERROR_LOG="$LOG_DIR/error.log"
VENV_DIR=".venv"

# Create log directory
mkdir -p $LOG_DIR

# Print colored output
print_success() {
    echo "✓ $1"
}

print_error() {
    echo "✗ $1"
}

print_info() {
    echo "ℹ $1"
}

# Start the application
start() {
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            print_error "App is already running (PID: $PID)"
            exit 1
        fi
    fi

    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv $VENV_DIR
    fi

    # Activate virtual environment
    source $VENV_DIR/bin/activate

    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        print_info "Checking dependencies..."
        pip install -q -r requirements.txt
    fi

    # Read port from .env (default to 5000)
    PORT=5000
    if [ -f ".env" ]; then
        PORT_VAL=$(grep "^PORT=" .env | cut -d '=' -f2)
        if [ ! -z "$PORT_VAL" ]; then
            PORT=$PORT_VAL
        fi
    fi

    print_info "Starting Claude Code API Wrapper..."
    # Start app in background with nohup
    nohup python $APP_FILE > $LOG_FILE 2> $ERROR_LOG &

    # Save PID to file
    echo $! > $PID_FILE

    print_success "Server started! (PID: $!)"
    print_info "URL: http://localhost:$PORT"
    print_info "Log: tail -f $LOG_FILE"
}

# Stop the application
stop() {
    if [ ! -f "$PID_FILE" ]; then
        print_error "Server is not running."
        exit 1
    fi

    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
        print_info "Stopping server (PID: $PID)..."
        kill $PID
        sleep 1

        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            print_info "Force killing server..."
            kill -9 $PID
        fi

        rm $PID_FILE
        print_success "Server stopped."
    else
        print_error "Process not found. Cleaning up PID file."
        rm $PID_FILE
        exit 1
    fi
}

# Check server status
status() {
    if [ ! -f "$PID_FILE" ]; then
        print_error "Server is NOT running."
        exit 1
    fi

    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
        print_success "Server is running (PID: $PID)"

        # Read port from .env
        PORT=5000
        if [ -f ".env" ]; then
            PORT_VAL=$(grep "^PORT=" .env | cut -d '=' -f2)
            if [ ! -z "$PORT_VAL" ]; then
                PORT=$PORT_VAL
            fi
        fi

        print_info "URL: http://localhost:$PORT"
    else
        print_error "Process not found (stale PID file). Cleaning up."
        rm $PID_FILE
        exit 1
    fi
}

# View logs
logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_error "Log file not found: $LOG_FILE"
        exit 1
    fi

    tail -f $LOG_FILE
}

# View error logs
errors() {
    if [ ! -f "$ERROR_LOG" ]; then
        print_error "Error log file not found: $ERROR_LOG"
        exit 1
    fi

    tail -f $ERROR_LOG
}

# Restart the application
restart() {
    if [ -f "$PID_FILE" ]; then
        stop
        sleep 2
    fi
    start
}

# Clean up old log files
clean() {
    print_info "Cleaning up log files..."
    rm -f $LOG_FILE $ERROR_LOG
    print_success "Log files cleaned."
}

# Print usage information
usage() {
    cat << EOF
Claude Code API Wrapper Management Script

Usage: ./manage.sh [COMMAND]

Commands:
  start       Start the application
  stop        Stop the application
  status      Check application status
  restart     Restart the application
  logs        View application logs (tail -f)
  errors      View error logs (tail -f)
  clean       Clean up log files
  help        Show this help message

Examples:
  ./manage.sh start
  ./manage.sh stop
  ./manage.sh status
  ./manage.sh restart
  ./manage.sh logs

EOF
}

# Main script logic
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    errors)
        errors
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac
