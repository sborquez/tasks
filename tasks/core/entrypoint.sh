#!/bin/sh

set -e

# Validate allowed commands
if [ "$TASK_COMMAND" = "tasks-run" ] || [ "$TASK_COMMAND" = "tasks-serve" ] || [ "$TASK_COMMAND" = "tasks-register" ]; then
    echo "Running: $TASK_COMMAND with arguments: $@"
    exec "$TASK_COMMAND" "$@"
else
    echo "Error: Invalid TASK_COMMAND value: '$TASK_COMMAND'"
    echo "Allowed values: tasks-run, tasks-serve, tasks-register"
    exit 1
fi