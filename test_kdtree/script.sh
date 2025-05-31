#!/bin/bash

iteration=1
while true; do
    echo "=== Iteration $iteration ==="
    echo "Running gen.py..."
    python3 gen.py

    echo "Running test.py..."
    python3 test.py < file.txt > out.txt

    echo "Running check.py..."
    output=$(python3 check.py)
    if [[ -n "$output" ]]; then
        echo "check.py output detected:"
        echo "$output"
        break
    else
        echo "check.py output is empty, repeating..."
    fi
    ((iteration++))
done