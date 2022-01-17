#!/usr/bin/env bash

for i in */; do
    echo "${i::-1}"
done