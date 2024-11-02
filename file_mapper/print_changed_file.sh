#!/bin/sh

# Capture the changed file name as the first argument
changed_file="$1"
relative_changed_file=$(realpath --relative-to="." "$changed_file")
# Use file_mapper.py to find the corresponding test file
mapped_test_file=$(python file_mapper.py "$relative_changed_file")
#echo $mapped_test_file
#
# Only run pytest if there’s a mapped test file
if [ -n "$mapped_test_file" ]; then
    echo "Running tests for $mapped_test_file"
    pytest $mapped_test_file
else
    echo "No test file mapped for $changed_file. Skipping pytest."
fi

