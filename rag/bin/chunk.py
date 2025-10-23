#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-22
  Purpose:
'''

import sys
import os
CWD = os.path.dirname(__file__)
sys.path.append(f"{CWD}/..")
sys.path.append(f"{CWD}/../..")

import argparse

from rag_base.chunk_tool import IterChunks


def get_params():
    ''' return dict for parameters '''
    parser = argparse.ArgumentParser(
        usage="",
        description=""
    )
    parser.add_argument(
        "-f", "--file", required=True, dest="file", type=str,
        default=None,
        help="a file path, if '-', file is /dev/stdin"
    )
    parser.add_argument(
        "-c", "--count", required=False, dest="count", type=int,
        default=3,
        help="print chunks with the count"
    )
    parser.add_argument(
        "-l", "--size", required=False, dest="size", type=int,
        default=1000,
        help="set chunk size"
    )
    parser.add_argument(
        "-s", "--separators", required=False, dest="separators", type=str,
        default=None,
        help="list_str, split by ','. example: '\\n\\n,)\\n\\n'"
    )

    args = parser.parse_args()
    params = {
        "file": args.file,
        "count": args.count,
        "size": args.size,
        "separators": args.separators,
    }
    if params["separators"]:
        params["separators"] = params["separators"].replace("\\n", "\n").replace("\\t", "\t").split(",")
    if params["file"] == "-":
        params["file"] = "/dev/stdin"

    return params

def main():
    """ main entry """
    params = get_params()
    print(params)
    print("====")
    count = 1
    for chunk in IterChunks(params["file"], params["size"], params["separators"]):
        print(f"\n[{count}]\n{chunk}")
        if count >= params["count"]:
            break
        count += 1
    return

if __name__ == "__main__":
    main()
