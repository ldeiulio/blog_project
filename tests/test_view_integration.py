import os
import unittest
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

import app
from database import Base, engine, db_session, User, Entry


class TestViews(unittest.TestCase):
    def setUp(self):
        """Test setup"""
        self.client = app.app.test_client()
        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        password = generate_password_hash("test")
        self.user = User(name="Alice", email="alice@example.com", password=password)
        db_session.add(self.user)
        db_session.commit()

    def tearDown(self):
        """Test teardown"""
        db_session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

    # tests if a correct login correctly logs in a user also determines if register works as a byproduct
    def test_correct_login(self):
        rv = self.login("alice@example.com", "test")
        self.assertIn(b'logged in', rv.data)

    # tests if an incorrect login does not flag the user as logged in and flashes the appropriate message
    def test_incorrect_login(self):
        rv = self.login("not@real.com", "asdf")
        self.assertNotIn(b'logged in', rv.data)
        self.assertIn(b'incorrect email or password', rv.data)

    # tests if an entry gets correctly added to the database
    def test_add_entry(self):
        self.login("alice@example.com", "test")
        self.add_entry("test", "test")
        entry = db_session.query(Entry).filter(Entry.user_id == self.user.id).first()
        self.assertNotEqual(entry, None, "Entry not created")
        self.assertEqual(entry.user_id, self.user.id, "user id's don't match")
        self.assertEqual("test", entry.content, "incorrect content")
        self.assertEqual("test", entry.title, "incorrect title")

    # tests if an entry that is edited gets correctly changed in the database and changes correctly
    def test_edit_entry(self):
        self.login("alice@example.com", "test")
        self.add_entry("test", "test")
        entry = db_session.query(Entry).filter(Entry.id == self.user.id).first()
        self.edit_entry("new title", "new body", entry.id)
        entry = db_session.query(Entry).filter(Entry.user_id == self.user.id).all()
        self.assertEqual(len(entry), 1)
        entry = entry[0]
        self.assertEqual(entry.user_id, self.user.id, "user id's don't match")
        self.assertEqual("new body", entry.content, "incorrect content")
        self.assertEqual("new title", entry.title, "incorrect title")

    # tests if viewing singular entry works correctly
    def test_view_entry(self):
        self.login("alice@example.com", "test")
        self.add_entry("view_test", "test_view")
        entry = db_session.query(Entry).filter(Entry.id == self.user.id).first()
        rv = self.view_entry(entry.id)
        self.assertIn(b'view_test', rv.data, "incorrect title or title is missing")
        self.assertIn(b'test_view', rv.data, "incorrect content or content is missing")

    # test if singular entry view properly updates after entry is edited
    def test_update_entry(self):
        self.test_view_entry()
        entry = db_session.query(Entry).filter(Entry.id == self.user.id).first()
        self.edit_entry("edited_title", "edited_body", entry.id)
        rv = self.view_entry(entry.id)
        self.assertIn(b'edited_title', rv.data, "title incorrectly updated")
        self.assertIn(b'edited_body', rv.data, "body incorrectly updated")

    # tests if deleting an entry properly removes an entry from database
    def test_delete_entry(self):
        self.login("alice@example.com", "test")
        self.add_entry("view_test", "test_view")
        entry = db_session.query(Entry).filter(Entry.id == self.user.id).first()
        rv = self.delete_entry(entry.id)
        self.assertIn(b'entry deleted', rv.data)
        entry = db_session.query(Entry).filter(Entry.id == self.user.id).first()
        self.assertIsNone(entry)

    # logs into supplied account for testing purposes
    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # adds in a test entry for testing purposes
    def add_entry(self, title, body):
        return self.client.post('/entry/add', data=dict(
            title=title,
            body=body
        ), follow_redirects=True)

    # edits entry tied to supplied id with supplied content for testing purposes
    def edit_entry(self, title, body, id):
        return self.client.post('entry/{}/edit'.format(id), data=dict(
            title=title,
            body=body
        ), follow_redirects=True)

    # goes to single entry view for given entry
    def view_entry(self, id):
        return self.client.get('entry/{}'.format(id))

    # deletes entry tied to supplied id
    def delete_entry(self, id):
        return self.client.post('entry/{}/delete'.format(id), data=dict(
            confirm="confirm"
        ), follow_redirects=True)

    # logs out user
    def logout(self):
        return self.client.get('logout', follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
