from bot.database.models import RuntimeState
from bot.database.session import get_session


def get_state(scope: str, key: str):
    session = get_session()
    try:
        row = session.query(RuntimeState).filter_by(scope=str(scope), state_key=str(key)).first()
        return row.value if row else None
    finally:
        session.close()


def set_state(scope: str, key: str, value) -> None:
    session = get_session()
    try:
        row = session.query(RuntimeState).filter_by(scope=str(scope), state_key=str(key)).with_for_update().first()
        if row:
            row.value = value
        else:
            session.add(RuntimeState(scope=str(scope), state_key=str(key), value=value))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_state(scope: str, key: str) -> None:
    session = get_session()
    try:
        session.query(RuntimeState).filter_by(scope=str(scope), state_key=str(key)).delete()
        session.commit()
    finally:
        session.close()
