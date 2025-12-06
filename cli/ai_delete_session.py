#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete a session by session ID

Usage:
    delete_session.py <session_id> [database_connection_string]

Arguments:
    session_id: Required session identifier to delete
    database_connection_string: Optional database connection string.
                                Defaults to 'sqlite:///memory.db'

Examples:
    delete_session.py abc123
    delete_session.py abc123 sqlite:///custom.db
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    sys.path.insert(0, project_root + "/src")

os.chdir(project_root)

from context.session_manager.sql import SessionSQLAlchemy


def main():
    # Check for required session_id argument
    if len(sys.argv) < 2:
        print("Error: session_id is required")
        print("Usage: delete_session.py <session_id> [database_connection_string]")
        sys.exit(1)

    session_id = sys.argv[1]

    # Get database connection from command line or use default
    db_conn = "sqlite:///memory.db"

    try:
        # Create manager
        manager = SessionSQLAlchemy(db_conn)

        # Check if session exists
        if not manager.exists_session(session_id):
            print(f"Error: Session '{session_id}' does not exist")
            sys.exit(1)

        # Delete session
        manager.delete_session(session_id)

        print(f"Session '{session_id}' has been successfully deleted")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
