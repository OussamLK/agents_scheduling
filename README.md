# How to run

run `uv run fastapi dev`

## stage 1

curl "http://127.0.0.1:8000/api/shifts/shf_1/available-agents"

## stage 2

curl "http://127.0.0.1:8000/api/shifts/shf_2/available-agents"

## stage 3

curl --json '{"agentId": "agt_3"}' "http://127.0.0.1:8000/api/shifts/shf_1/assignments"