#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  Unit tests for session_manager sql
'''

import pytest
import sys
import os
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)
from context.session_manager.sql import SessionSQLAlchemy, SessionData

class TestSessionSQLAlchemy:
    @pytest.fixture
    def db_conn(self):
        return "sqlite:///:memory:"

    @pytest.fixture
    def manager(self, db_conn):
        return SessionSQLAlchemy(db_conn)

    def test_create_session_basic(self, manager):
        # Create a session
        session_data = SessionData("session1", "Test task")
        session_data.session_name = "Test Session"
        manager.create_session(session_data)

        # Verify it was created
        sessions = manager.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].session_id == "session1"
        assert sessions[0].task == "Test task"
        assert sessions[0].session_name == "Test Session"
        assert sessions[0].create_time is not None

    def test_create_session_session_limit(self, manager):
        # Create 105 sessions
        for i in range(105):
            session_data = SessionData(f"session{i}", f"Task {i}")
            session_data.session_name = f"Session {i}"
            manager.create_session(session_data)

        # Verify only 100 sessions remain (the most recent ones)
        sessions = manager.list_sessions()
        assert len(sessions) == 100

        # Check that the oldest ones (0-4) are gone and newest ones (5-104) remain
        session_ids = {session.session_id for session in sessions}
        # Sessions 0-4 should not be present
        assert "session0" not in session_ids
        assert "session1" not in session_ids
        assert "session2" not in session_ids
        assert "session3" not in session_ids
        assert "session4" not in session_ids
        # Sessions 5-104 should be present
        assert "session5" in session_ids
        assert "session100" in session_ids
        assert "session104" in session_ids

    def test_list_sessions_empty(self, manager):
        sessions = manager.list_sessions()
        assert sessions == []

    def test_list_sessions_ordering(self, manager):
        # Create sessions with different creation times (simulated by creating them in order)
        import time
        for i in range(5):
            session_data = SessionData(f"session{i}", f"Task {i}")
            manager.create_session(session_data)
            time.sleep(0.01)  # Small delay to ensure different timestamps

        sessions = manager.list_sessions()
        assert len(sessions) == 5
        # Should be ordered by create_time descending (newest first)
        assert sessions[0].session_id == "session4"
        assert sessions[1].session_id == "session3"
        assert sessions[2].session_id == "session2"
        assert sessions[3].session_id == "session1"
        assert sessions[4].session_id == "session0"

    def test_create_session_without_name(self, manager):
        # Create session without session_name
        session_data = SessionData("session1", "Test task")
        manager.create_session(session_data)

        sessions = manager.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].session_name is None

    def test_create_session_duplicate_id(self, manager):
        # Create first session
        session_data1 = SessionData("session1", "Task 1")
        manager.create_session(session_data1)

        # Try to create another with same ID (should raise error due to primary key constraint)
        session_data2 = SessionData("session1", "Task 2")
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            manager.create_session(session_data2)

        # Should still have only one session
        sessions = manager.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].task == "Task 1"
