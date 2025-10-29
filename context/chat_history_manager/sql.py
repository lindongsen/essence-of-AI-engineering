'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-29
  Purpose: using sqlalchemy to manage chat history messages of AI Agent.
  Schema:
    - table_name: chat_history_messages
      - columns:
        - msg_id, text, it is primary key;
        - message, text, the message content;
        - create_time, the creation time of this record;
        - msg_size,  length of message;
        - access_time, last access time; update access time when querying by msg_id.
        - access_count, count of retrieval; default is 0, The count increases by 1 with each retrieve when querying by msg_id.
    - table_name: map_session_message
      - columns: primary_key(msg_id, session_id)
        - msg_id: it is from table chat_history_messages;
        - session_id: text
        - create_time, the creation time of this record;

  Function:
    - add_message(session_id, message), add a record to table chat_history_messages;
    - get_message(msg_id), get record from table chat_history_messages;
    - get_messages_by_session(session_id), get records from table chat_history_messages;
    - del_messages(msg_id, session_id), del records from table chat_history_messages and map_session_message;
        If a session_id is provided, it is necessary to check the count of records in the map_session_message for each msg_id associated with that session_id.
        If the count is 0 for a particular msg_id, that msg_id should be deleted from chat_history_messages.
'''

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

from .__base import ChatHistoryBase, ChatHistoryMessageData
from logger.log_chat import logger


Base = declarative_base()

class Message(Base):
    """
    Represents a chat history message in the database.

    Attributes:
        msg_id (str): Unique identifier for the message (primary key).
        message (str): The content of the message.
        create_time (datetime): Timestamp when the message was created.
        msg_size (int): Length of the message.
        access_time (datetime): Last access time, updated when queried by msg_id.
        access_count (int): Number of times the message has been retrieved.
        sessions (relationship): Relationship to SessionMessage instances.
    """
    __tablename__ = ChatHistoryBase.tb_chat_history_messages

    msg_id = Column(String(32), primary_key=True)
    message = Column(Text, nullable=False)
    create_time = Column(DateTime, default=datetime.now())
    msg_size = Column(Integer, nullable=False)
    access_time = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0, nullable=False)

    # Relationship to sessions
    sessions = relationship("SessionMessage", back_populates="message")

class SessionMessage(Base):
    """
    Maps messages to sessions in the database.

    Attributes:
        msg_id (str): Foreign key to Message.msg_id.
        session_id (str): Identifier for the session.
        create_time (datetime): Timestamp when the mapping was created.
        message (relationship): Relationship back to the Message instance.
    """
    __tablename__ = ChatHistoryBase.tb_map_session_message

    msg_id = Column(String(32), ForeignKey('chat_history_messages.msg_id'), nullable=False)
    session_id = Column(String, nullable=False)
    create_time = Column(DateTime, default=datetime.now())

    __table_args__ = (
        PrimaryKeyConstraint('msg_id', 'session_id'),
    )

    # Relationship back to message
    message = relationship("Message", back_populates="sessions")

class ChatHistorySQLAlchemy(ChatHistoryBase):
    """
    A SQLAlchemy-based implementation of ChatHistoryBase for managing chat history.

    This class provides methods to add, retrieve, and delete chat messages,
    managing the relationship between messages and sessions.

    Attributes:
        engine: SQLAlchemy engine instance.
        SessionLocal: Session factory for database operations.
    """
    def __init__(self, conn:str):
        """
        Initialize the ChatHistorySQLAlchemy instance with the given database connection string.

        Args:
            conn (str): Database connection string.
        """
        super(ChatHistorySQLAlchemy, self).__init__()
        self.engine = create_engine(conn)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def add_message(self, msg: ChatHistoryMessageData):
        """
        Add a message to the storage if it doesn't exist, and create a session mapping.

        If the message with the given msg_id already exists, it won't be re-added.
        Always adds a mapping between the message and the session, if not already present.

        Args:
            msg (ChatHistoryMessageData): The message data to add, including msg_id, message, and session_id.
        """

        session = self.SessionLocal()
        try:
            # Check if message exists
            existing_message = session.query(Message).filter(Message.msg_id == msg.msg_id).first()
            if not existing_message:
                # Insert new message
                new_message = Message(
                    msg_id=msg.msg_id,
                    message=msg.message,
                    msg_size=len(msg.message),
                    access_time=None,
                    access_count=0
                )
                session.add(new_message)

            # Check if session mapping exists
            existing_mapping = session.query(SessionMessage).filter(
                SessionMessage.msg_id == msg.msg_id,
                SessionMessage.session_id == msg.session_id
            ).first()
            if not existing_mapping:
                new_mapping = SessionMessage(
                    msg_id=msg.msg_id,
                    session_id=msg.session_id
                )
                session.add(new_mapping)

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"add_messages failed: {e}")
            raise e
        finally:
            session.close()

    def get_message(self, msg_id) -> ChatHistoryMessageData:
        """
        Retrieve a single message by its msg_id and update access metadata.

        Updates the access_time to current time and increments access_count.

        Args:
            msg_id (str): The unique identifier of the message to retrieve.

        Returns:
            ChatHistoryMessageData: The message data object, or None if not found.
        """
        session = self.SessionLocal()
        message = None
        try:
            message = session.query(Message).filter(Message.msg_id == msg_id).first()
            if message:
                # Update access_time and access_count
                message.access_time = datetime.now()
                message.access_count += 1
                session.commit()

                # Populate ChatHistoryMessageData
                data = ChatHistoryMessageData(
                    message=message.message,
                    msg_id=message.msg_id,
                    session_id=None  # Will be set when getting sessions
                )
                data.msg_size = message.msg_size
                data.create_time = message.create_time
                data.access_time = message.access_time
                data.access_count = message.access_count
                return data
            else:
                return None
        except Exception as e:
            session.rollback()
            logger.error(f"get_message failed: msg_id={msg_id}, {e}")
            raise e
        finally:
            session.close()


    def get_messages_by_session(self, session_id) -> list[ChatHistoryMessageData]:
        """
        Retrieve all messages associated with a specific session, ordered by creation time (descending).

        Args:
            session_id (str): The session identifier to filter messages.

        Returns:
            list[ChatHistoryMessageData]: List of message data objects for the session.
        """
        session = self.SessionLocal()
        try:
            # Query SessionMessage with join to Message
            results = session.query(SessionMessage, Message).join(
                Message, SessionMessage.msg_id == Message.msg_id
            ).filter(SessionMessage.session_id == session_id).order_by(SessionMessage.create_time.asc()).all()

            messages = []
            for mapping, message in results:
                # Populate ChatHistoryMessageData
                data = ChatHistoryMessageData(
                    message=message.message,
                    msg_id=message.msg_id,
                    session_id=mapping.session_id
                )
                data.msg_size = message.msg_size
                data.create_time = message.create_time
                data.access_time = message.access_time
                data.access_count = message.access_count
                messages.append(data)
            return messages
        except Exception as e:
            session.rollback()
            logger.error(f"get_messages_by_session failed: session_id={session_id}, {e}")
            raise e
        finally:
            session.close()

    def update_message_access(self, msg_id):
        """
        Update the access metadata for a message: set access_time to current time and increment access_count.

        Args:
            msg_id (str): The unique identifier of the message to update.
        """
        session = self.SessionLocal()
        try:
            session.query(Message).filter(Message.msg_id == msg_id).update({
                Message.access_time: datetime.now(),
                Message.access_count: Message.access_count + 1
            })
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"update_message failed: msg_id={msg_id}, {e}")
            raise e
        finally:
            session.close()

    def del_messages(self, msg_id=None, session_id=None):
        """
        Delete messages from storage based on msg_id or session_id.

        If session_id is provided, deletes all mappings for that session and any orphaned messages
        (messages no longer mapped to any session). If msg_id is provided, deletes all mappings
        for that message and the message itself. At least one of msg_id or session_id must be provided.

        Args:
            msg_id (str, optional): The message ID to delete all instances of.
            session_id (str, optional): The session ID to delete all messages for.

        Raises:
            AssertionError: If neither msg_id nor session_id is provided.
        """
        assert msg_id or session_id
        session = self.SessionLocal()
        try:
            # Delete mappings
            delete_query = session.query(SessionMessage)
            if msg_id:
                delete_query = delete_query.filter(SessionMessage.msg_id == msg_id)
            if session_id:
                delete_query = delete_query.filter(SessionMessage.session_id == session_id)

            mappings_to_delete = delete_query.all()

            # Collect msg_ids that might need deletion
            msg_ids_to_check = set()
            for mapping in mappings_to_delete:
                msg_ids_to_check.add(mapping.msg_id)
                session.delete(mapping)

            session.flush()  # Flush to ensure deletions are visible

            # Check for each msg_id if it has any remaining mappings
            for msg_id_to_check in msg_ids_to_check:
                remaining_count = session.query(SessionMessage).filter(SessionMessage.msg_id == msg_id_to_check).count()
                if remaining_count == 0:
                    msg_to_delete = session.query(Message).filter(Message.msg_id == msg_id_to_check).first()
                    if msg_to_delete:
                        session.delete(msg_to_delete)

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("del_messages failed: msg_id={msg_id}, session_id={session_id}, {e}")
            raise e
        finally:
            session.close()


MANAGERS = dict(
    ChatHistorySQLAlchemy=ChatHistorySQLAlchemy,
)
