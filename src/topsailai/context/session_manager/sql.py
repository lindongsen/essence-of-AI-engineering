'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-29
  Purpose: using sqlalchemy to manage session.
  Schema:
    - table_name: session
    - columns:
      - session_id, text, the session id;
      - session_name, text;
      - task, text, the task info;
      - create_time, creation time of this record; default is local time;
'''

from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

from topsailai.context.chat_history_manager.sql import ChatHistorySQLAlchemy
from topsailai.logger.log_chat import logger

from .__base import SessionStorageBase, SessionData

Base = declarative_base()

class Session(Base):
    """
    Represents a session in the database.

    Attributes:
        session_id (str): Unique identifier for the session (primary key).
        session_name (str): Name of the session.
        task (str): Task information for the session.
        create_time (datetime): Timestamp when the session was created.
    """
    __tablename__ = SessionStorageBase.tb_session

    session_id = Column(String(32), primary_key=True)
    session_name = Column(String, nullable=True)
    task = Column(Text, nullable=False)
    create_time = Column(DateTime, default=datetime.now())

class SessionSQLAlchemy(SessionStorageBase):
    """
    A SQLAlchemy-based implementation of SessionStorageBase for managing sessions.

    This class provides methods to create and manage sessions.

    Attributes:
        engine: SQLAlchemy engine instance.
        SessionLocal: Session factory for database operations.
    """

    def __init__(self, conn:str):
        """
        Initialize the SessionSQLAlchemy instance with the given database connection string.

        Args:
            conn (str): Database connection string.
        """
        super(SessionSQLAlchemy, self).__init__()
        self.engine = create_engine(conn)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        self.chat_history = ChatHistorySQLAlchemy(conn)

    def create_session(self, session_data:SessionData):
        """
        Create a new session in the storage and keep only the most recent 100 sessions.

        Args:
            session_data (SessionData): The session data to create.
        """
        db_session = self.SessionLocal()
        try:
            new_session = Session(
                session_id=session_data.session_id,
                session_name=session_data.session_name,
                task=session_data.task,
                create_time=session_data.create_time or datetime.now()
            )
            db_session.add(new_session)
            db_session.commit()
            logger.info(f"new session: session_id={session_data.session_id}, task={session_data.task}")

            # Keep only the most recent 100 sessions
            total_count = db_session.query(Session).count()
            if total_count > 100:
                # Delete the oldest sessions to keep only 100
                sessions_to_delete = db_session.query(Session).order_by(Session.create_time.asc()).limit(total_count - 100).all()
                for session in sessions_to_delete:
                    db_session.delete(session)
                    self.chat_history.del_messages(session_id=session.session_id)
                db_session.commit()
                logger.info(f"clear oldest sessions")
        except Exception as e:
            db_session.rollback()
            logger.error(f"create_session failed: {e}")
            raise e
        finally:
            db_session.close()

    def list_sessions(self) -> list[SessionData]:
        """
        List all sessions from the storage.

        Returns:
            list[SessionData]: List of all session data objects, ordered by creation time (descending).
        """
        db_session = self.SessionLocal()
        try:
            sessions = db_session.query(Session).order_by(Session.create_time.desc()).all()
            result = []
            for session in sessions:
                session_data = SessionData(
                    session_id=session.session_id,
                    task=session.task
                )
                session_data.session_name = session.session_name
                session_data.create_time = session.create_time
                result.append(session_data)
            return result
        except Exception as e:
            db_session.rollback()
            logger.error(f"list_sessions failed: {e}")
            raise e
        finally:
            db_session.close()

    def exists_session(self, session_id) -> bool:
        """
        Check if a session with the given session_id exists.

        Args:
            session_id (str): The session id to check.

        Returns:
            bool: True if the session exists, False otherwise.
        """
        db_session = self.SessionLocal()
        try:
            session = db_session.query(Session).filter(Session.session_id == session_id).first()
            return session is not None
        except Exception as e:
            db_session.rollback()
            logger.error(f"exists_session failed: {e}")
            raise e
        finally:
            db_session.close()

    def retrieve_messages(self, session_id:str) -> list[dict]:
        """ retrieve messages for session """
        return self.chat_history.retrieve_messages(session_id)

    def delete_session(self, session_id: str):
        """
        Delete a session and its associated chat history.

        Args:
            session_id (str): The session id to delete.

        Raises:
            Exception: If the session does not exist or deletion fails.
        """
        db_session = self.SessionLocal()
        try:
            # Check if session exists
            session = db_session.query(Session).filter(Session.session_id == session_id).first()
            if not session:
                raise Exception(f"Session {session_id} does not exist")

            # Delete the session
            db_session.delete(session)

            # Delete associated chat history
            self.chat_history.del_messages(session_id=session_id)

            db_session.commit()
            logger.info(f"Session deleted: session_id={session_id}")

        except Exception as e:
            db_session.rollback()
            logger.error(f"delete_session failed: session_id={session_id}, {e}")
            raise e
        finally:
            db_session.close()
