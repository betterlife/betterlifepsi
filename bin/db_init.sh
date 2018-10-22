#!/bin/bash
DBS_TO_CREATE=(
    psi
    psi_test
)

for db in "${DBS_TO_CREATE[@]}"; do
    createdb "$db" -E utf8 -l en_US.utf8 -T template0
done
