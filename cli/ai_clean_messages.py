#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean old messages from chat history

Usage:
    ai_clean_messages.py [before_seconds] [database_connection_string]

Arguments:
    before_seconds: Optional number of seconds before current time.
                   Messages with access_time less than (current time - before_seconds) will be deleted.
                   Defaults to 2592000 (30 days).
    database_connection_string: Optional database connection string.
                               Defaults to 'sqlite:///memory.db'

Examples:
    ai_clean_messages.py
    ai_clean_messages.py 86400
    ai_clean_messages.py 604800 sqlite:///custom.db
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root + "/src")

os.chdir(project_root)

from topsailai.context.chat_history_manager.sql import ChatHistorySQLAlchemy


def main():
    # Default values
    default_before_seconds = 30 * 24 * 60 * 60  # 30 days in seconds
    default_db_conn = "sqlite:///memory.db"

    # Parse command line arguments
    before_seconds = default_before_seconds
    db_conn = default_db_conn

    if len(sys.argv) > 1:
        try:
            before_seconds = int(sys.argv[1])
            if before_seconds <= 0:
                print("Error: before_seconds must be a positive integer")
                sys.exit(1)
        except ValueError:
            print("Error: before_seconds must be a valid integer")
            sys.exit(1)

    if len(sys.argv) > 2:
        db_conn = sys.argv[2]

    try:
        # Create manager
        manager = ChatHistorySQLAlchemy(db_conn)

        # Clean messages
        deleted_count = manager.clean_messages(before_seconds)

        # Calculate cutoff time for display
        cutoff_time = datetime.now() - timedelta(seconds=before_seconds)

        print(f"Successfully cleaned {deleted_count} messages")
        print(f"Cutoff time: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Messages older than {before_seconds} seconds ({before_seconds // 86400} days) have been deleted")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
