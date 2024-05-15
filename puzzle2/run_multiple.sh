#!/bin/bash
set -Eeo pipefail
# Define arrays of input, goal and output files
input_files=("inputs/sample_input0.txt" "inputs/sample_input1.txt" "inputs/sample_input2.txt" "inputs/sample_input3.txt")
output_files=("outputs/output0.txt" "outputs/output1.txt" "outputs/output2.txt" "outputs/output3.txt")
goal_files=("goals/sample_output0.txt" "goals/sample_output1.txt" "goals/sample_output2.txt" "goals/sample_output3.txt")
# Loop through arrays
# > /dev/null 2>&1
for i in ${!input_files[@]}; do
    python3 puzzle2.py ${input_files[$i]} ${output_files[$i]}
    wait

    # Compare the output with the goal file
    if ! diff "${output_files[$i]}" "${goal_files[$i]}" > /dev/null; then
        echo "Error: Output for ${input_files[$i]} does not match the goal file."
    fi
done