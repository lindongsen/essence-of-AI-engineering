#!/bin/bash

set -e

CPATH=$(readlink -f "$0")
CWD=$(dirname "${CPATH}")
cd "${CWD}"

TEST_FILE="../idea_for_abstract/rag/txt/t-ara.txt"
TEST_CONTENT=$(head -5 ${TEST_FILE})
TEST_DB_NAME="tiara"

set -x
uv run ./abstract.py -t "${TEST_CONTENT}" -m "eboafour1/bertsum"
uv run ./chunk.py -f "${TEST_FILE}"
uv run ./embedding.py -f "${TEST_FILE}" -d "${TEST_DB_NAME}"
uv run ./query.py -q "T-ARA有哪些作品" -d "$PWD/rag_db" -i "${TEST_DB_NAME}"
