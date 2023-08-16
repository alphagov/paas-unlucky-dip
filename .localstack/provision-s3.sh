#!/usr/bin/env bash

awslocal s3api \
    create-bucket --bucket my-bucket \
    --create-bucket-configuration LocationConstraint=eu-west-2 \
    --region eu-west-2
