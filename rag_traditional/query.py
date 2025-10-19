#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-17
  Purpose:
'''

import sys
import os
CWD = os.path.dirname(__file__)
sys.path.append(f"{CWD}/..")

import time
import argparse

from utils.db_tool import DBClient
from utils.file_tool import get_filename
from utils.print_tool import print_with_time

from ai_base import rag_base


def get_params():
    ''' return dict for parameters '''
    parser = argparse.ArgumentParser(
        usage="",
        description=""
    )
    parser.add_argument(
        "-q", "--question", required=True, dest="question", type=str,
        default=None,
        help=""
    )
    parser.add_argument(
        "-d", "--db_file", required=True, dest="db_file", type=str,
        default=None,
        help=""
    )
    parser.add_argument(
        "-i", "--index_name", required=False, dest="index_name", type=str,
        default=None,
        help="collection name"
    )
    args = parser.parse_args()
    params = {
        "question": args.question,
        "db_file": args.db_file,
        "index_name": args.index_name,
    }
    return params

def print_chunks(chunks):
    """ just print chunks """
    for i, chunk in enumerate(chunks):
        print(f"[{i}]\n{chunk}\n")

def main():
    """ main entry """
    params = get_params()

    name = params["index_name"] or get_filename(params["db_file"])
    db = DBClient(conn={"protocol": "file", "path": params["db_file"]})

    rag_ctler = rag_base.RAGCtler(db)

    start_ts = time.time()

    print_with_time(">>> retrieving ...")
    chunks = rag_ctler.retrieve(params["question"], name, 10)
    print_with_time(">>> retrieved")
    print_chunks(chunks)

    print_with_time(">>> reranking ...")
    chunks = rag_ctler.rerank(params["question"], chunks, 3)
    print_with_time(">>> reranked")
    print_chunks(chunks)

    print_with_time(">>> done")

    end_ts = time.time()

    print_with_time(f"[ElapsedTime] {end_ts-start_ts}")
    return


if __name__ == "__main__":
    main()
