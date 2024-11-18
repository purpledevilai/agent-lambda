#!/bin/bash

# Docker build
docker build -t agent_lambda_test_image .

# Docker run
docker run \
--env-file .env \
-v ./:/app \
-d \
--name agent_lambda_test_container \
recomendation_engine_test_image

# Launch bash
docker exec -it agent_lambda_test_container bash