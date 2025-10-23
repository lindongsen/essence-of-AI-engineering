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
sys.path.append(f"{CWD}/../..")

import time
import argparse

from utils.file_tool import get_filename
from utils.print_tool import print_with_time

from rag_base.chunk_tool import IterChunks
from rag_base.db_tool import DBClient


def get_params():
    ''' return dict for parameters '''
    parser = argparse.ArgumentParser(
        usage="",
        description=""
    )
    parser.add_argument(
        "-f", "--file", required=True, dest="file", type=str,
        default=None,
        help="file path"
    )
    parser.add_argument(
        "-d", "--db", required=True, dest="db", type=str,
        default=None,
        help="database name"
    )
    args = parser.parse_args()
    params = {
        "file": args.file,
        "db": args.db,
    }
    return params

def main():
    """ main entry """
    params = get_params()

    db_name = params["db"]
    if not db_name:
        db_name = get_filename(params["file"])
    db = DBClient(conn={"protocol": "file", "path": f"{CWD}/rag_db"})

    start_ts = time.time()

    print_with_time(">>> embedding ...")
    from rag_base import rag_base
    for i, chunk in enumerate(IterChunks(params["file"])):
        embedding = rag_base.embed_chunk(chunk)
        print(f"[{i}]\n{chunk}")
        print(f"[embedding] {embedding[0]} ...(force to truncate)")
        print("\n")
        db.save_embeddings(db_name, [chunk], [embedding])

    print_with_time(">>> done")

    end_ts = time.time()

    print_with_time(f"[ElapsedTime] {end_ts-start_ts}")
    return

if __name__ == "__main__":
    main()
