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

from utils.print_tool import print_with_time


def get_params():
    ''' return dict for parameters '''
    parser = argparse.ArgumentParser(
        usage="",
        description=""
    )
    parser.add_argument(
        "-t", "--text", required=False, dest="text", type=str,
        default=None,
        help=""
    )
    parser.add_argument(
        "-m", "--model", required=False, dest="model", type=str,
        default="google/pegasus-large",
        help=""
    )
    args = parser.parse_args()
    params = {
        "text": args.text,
        "model": args.model,
    }
    return params

def main():
    """ main entry """
    params = get_params()

    from ai_base import rag_base
    rag_ctler = rag_base.RAGCtler(None)

    print_with_time(f">>> generating with model={params['model']} ...")

    input_str = params["text"]
    while True:
        if not input_str:
            input_str = input("\nEnter Text: ")
        if not input_str.strip():
            continue
        if input_str.lower() in ["exit", "quit"]:
            break
        start_ts = time.time()
        summary = rag_ctler.generate_abstract(input_str, params["model"])
        print(">>>\n"+summary+"\n<<<")
        end_ts = time.time()
        print_with_time(f"[ElapsedTime] {end_ts-start_ts}")
        if params["text"]:
            # run once
            break
        # continue
        input_str = ""

    print_with_time(">>> done")


    return


if __name__ == "__main__":
    main()
