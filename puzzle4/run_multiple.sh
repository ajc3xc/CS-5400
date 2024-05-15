#!/bin/bash
set -Eeo pipefail
# Define arrays of input, goal and output files
input_files=("samples/sampledungeon0.txt" "samples/sampledungeon1.txt" "samples/sampledungeon2.txt" "samples/sampledungeon3.txt")
output_files=("outputs/output0.txt" "outputs/output1.txt" "outputs/output2.txt" "outputs/output3.txt")
goal_files=("samples/sampleoutput0.txt" "samples/sampleoutput1.txt" "samples/sampleoutput2.txt" "samples/sampleoutput3.txt")
# Loop through arrays
# > /dev/null 2>&1
for i in ${!input_files[@]}; do
    #> /dev/null 2>&1
    python3 puzzle4.py ${input_files[$i]} ${output_files[$i]}
    wait

    # Compare the output with the goal file
    if ! diff "${output_files[$i]}" "${goal_files[$i]}" > /dev/null; then
        echo "Error: Output for ${input_files[$i]} does not match the goal file."
    fi
done