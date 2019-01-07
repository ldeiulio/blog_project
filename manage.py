from database import db_session, Entry
from flask_script import Manager
from database import app


manager = Manager(app)
print(__name__)


@manager.command
def seed():
    content = """
    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore 
    et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla 
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est 
    laborum.
    """
    print("test")
    for i in range(25):
        entry = Entry(
            title="Test Entry #{}".format(i),
            content=content,
            user_id=1
        )
        db_session.add(entry)
    db_session.commit()


if __name__ == "__main__":
    manager.run()
