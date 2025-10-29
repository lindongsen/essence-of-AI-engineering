#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List all sessions from the session database

Usage:
    list_sessions.py [database_connection_string]

Arguments:
    database_connection_string: Optional database connection string.
                                Defaults to 'sqlite:///sessions.db'

Examples:
    list_sessions.py
    list_sessions.py sqlite:///custom.db
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.chdir(project_root)

from context.session_manager.sql import SessionSQLAlchemy


def format_sessions(sessions):
    """Format sessions for display"""
    if not sessions:
        return "No sessions found."

    # Header
    output = []
    output.append("Sessions:")
    output.append("-" * 80)
    output.append("SESSION_ID".ljust(35) + "NAME".ljust(25) + "CREATED")
    output.append("-" * 80)

    # Sessions
    for session in sessions:
        session_id = str(session.session_id)[:34]
        name = (str(session.session_name) if session.session_name else '')[:24]
        created = session.create_time.strftime("%Y-%m-%d %H:%M:%S") if session.create_time else ''
        output.append(f"{session_id.ljust(35)}{name.ljust(25)}{created}")
        output.append(f"  Task: {session.task[:65]}{'...' if len(session.task) > 65 else ''}")

    output.append("-" * 80)
    output.append(f"Total: {len(sessions)} sessions")

    return '\n'.join(output)


def main():
    # Get database connection from command line or use default
    db_conn = "sqlite:///memory.db"

    try:
        # Create manager
        manager = SessionSQLAlchemy(db_conn)

        # List sessions
        sessions = manager.list_sessions()

        # Display results
        formatted_output = format_sessions(sessions)
        print(formatted_output)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
