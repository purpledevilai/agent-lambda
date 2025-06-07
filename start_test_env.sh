#!/bin/bash

# Docker build
docker build --no-cache -t agent_lambda_test_image .

# Docker run
docker run \
--env-file .env \
-v ./:/app \
-d \
--name agent_lambda_test_container \
agent_lambda_test_image

# Launch bash
docker exec -it agent_lambda_test_container bash