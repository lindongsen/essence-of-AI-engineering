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
        "-f", "--file", required=True, dest="file", type=str,
        default=None,
        help=""
    )
    args = parser.parse_args()
    params = {
        "file": args.file,
    }
    return params

def main():
    """ main entry """
    params = get_params()

    name = get_filename(params["file"])
    db = DBClient(conn={"protocol": "file", "path": f"{CWD}/{name}.db"})

    start_ts = time.time()

    print_with_time(">>> embedding ...")
    for i, chunk in enumerate(rag_base.IterChunks(params["file"])):
        embedding = rag_base.embed_chunk(chunk)
        print(f"[{i}]\n{chunk}")
        print("[embedding] %s ..." % embedding[0])
        print("\n")
        db.save_embeddings(name, [chunk], [embedding])

    print_with_time(">>> done")

    end_ts = time.time()

    print_with_time(f"[ElapsedTime] {end_ts-start_ts}")
    return

if __name__ == "__main__":
    main()
