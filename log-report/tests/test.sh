#!/bin/bash

# pytest is baked into the environment image (environment/Dockerfile).
mkdir -p /logs/verifier
pytest /tests/test_outputs.py -rA --ctrf /logs/verifier/ctrf.json

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
