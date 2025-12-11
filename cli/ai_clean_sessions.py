#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean old sessions from session storage

Usage:
    ai_clean_sessions.py [before_seconds] [database_connection_string]

Arguments:
    before_seconds: Optional number of seconds before current time.
                   Sessions with create_time less than (current time - before_seconds) will be deleted.
                   Defaults to 2592000 (30 days).
    database_connection_string: Optional database connection string.
                               Defaults to 'sqlite:///memory.db'

Examples:
    ai_clean_sessions.py
    ai_clean_sessions.py 86400
    ai_clean_sessions.py 604800 sqlite:///custom.db
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root + "/src")

os.chdir(project_root)

from topsailai.context.session_manager.sql import SessionSQLAlchemy


def main():
    # Default values
    default_before_seconds = 30 * 24 * 60 * 60  # 30 days in seconds (1 month)
    default_db_conn = "sqlite:///memory.db"

    # Parse command line arguments
    before_seconds = default_before_seconds
    db_conn = default_db_conn

    if len(sys.argv) > 1:
        try:
            before_seconds = int(sys.argv[1])
            if before_seconds < 0:
                print("Error: before_seconds must be a non-negative integer")
                sys.exit(1)
        except ValueError:
            print("Error: before_seconds must be a valid integer")
            sys.exit(1)

    if len(sys.argv) > 2:
        db_conn = sys.argv[2]

    try:
        # Create manager
        manager = SessionSQLAlchemy(db_conn)

        # Clean sessions
        deleted_count = manager.clean_sessions(before_seconds)

        # Calculate cutoff time for display
        cutoff_time = datetime.now() - timedelta(seconds=before_seconds)

        print(f"Successfully cleaned {deleted_count} sessions")
        print(f"Cutoff time: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sessions older than {before_seconds} seconds ({before_seconds // 86400} days) have been deleted")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
