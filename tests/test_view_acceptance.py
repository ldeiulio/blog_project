import os
import unittest
import multiprocessing
import time

from werkzeug.security import generate_password_hash
from splinter import Browser

# configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"
from app import app
from database import Base, engine, db_session, User


class TestViews(unittest.TestCase):
    def setUp(self):
        """Test Setup"""
        self.browser = Browser('firefox', headless=True)

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        password = generate_password_hash("test")
        self.user = User(name="Alice", email="alice@example.com", password=password)
        db_session.add(self.user)
        db_session.commit()

        self.process = multiprocessing.Process(target=app.run, kwargs={"port": 8080})
        self.process.start()
        time.sleep(1)

    def tearDown(self):
        """Test teardown"""
        self.process.terminate()
        db_session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()

    # tests if a correct login works as intended via browser
    def test_login_correct(self):
        self.visit_site()
        self.assertTrue(self.browser.is_element_not_present_by_text("Log out"))
        self.login("alice@example.com", "test")
        self.assertFalse(self.browser.is_element_not_present_by_text("Log out"))
        self.assertTrue(self.browser.is_element_present_by_css('.flash'), "no message flashed")
        msg = self.browser.find_by_css('.flash').first
        self.assertEqual(msg.text, "logged in", "incorrect message flashed")

    # tests if an incorrect login would appropriately fail the attempt as intended
    def test_login_incorrect(self):
        self.visit_site()
        self.assertTrue(self.browser.is_element_not_present_by_text("Log out"))
        self.login("notan@email.com", "asdf")
        self.assertTrue(self.browser.is_element_not_present_by_text("Log out"))
        self.assertTrue(self.browser.is_element_present_by_css('.flash'), "no message flashed")
        msg = self.browser.find_by_css('.flash').first
        self.assertEqual(msg.text, "incorrect email or password", "incorrect message flashed")

    # tests if adding an entry as a user works as intended
    def test_add_entry(self):
        self.visit_site()
        self.login("alice@example.com", "test")
        self.add_entry("test title", "test body")
        self.assertTrue(self.browser.is_element_present_by_text("test title"), "no post with correct title")
        self.assertTrue(self.browser.is_element_present_by_text("test body"), "no post with correct body")

    # tests  if an edited entry correctly displays as expected
    def test_edit_entry(self):
        self.visit_site()
        self.login("alice@example.com", "test")
        self.add_entry("test title", "test body")
        self.edit_entry("edited title","edited body")
        self.assertTrue(self.browser.is_element_present_by_text("edited title"), "no post with correct title")
        self.assertTrue(self.browser.is_element_present_by_text("edited body"), "no post with correct body")
        self.assertFalse(self.browser.is_element_present_by_text("test title"), "old title still exists")
        self.assertFalse(self.browser.is_element_present_by_text("test body"), "old body still exists")

    # tests if clicking on an entry title correctly directs and displays the single entry
    def test_view_entry(self):
        self.visit_site()
        self.login("alice@example.com", "test")
        self.add_entry("test title", "test body")
        self.view_entry("test title")
        self.assertTrue(self.browser.is_element_present_by_text("test title"), "no post with correct title")
        self.assertTrue(self.browser.is_element_present_by_text("test body"), "no post with correct body")

    # tests if an edited entry correctly updates when viewed as a single entry
    def test_update_entry(self):
        self.test_view_entry()
        self.edit_entry("edited title", "edited body")
        self.view_entry("edited title")
        self.assertTrue(self.browser.is_element_present_by_text("edited title"), "no post with correct title")
        self.assertTrue(self.browser.is_element_present_by_text("edited body"), "no post with correct body")

    # tests if an added entry can correctly be deleted
    def test_delete_entry(self):
        self.test_add_entry()
        self.delete_entry()
        msg = self.browser.find_by_css('.flash').first
        self.assertEqual(msg.text, "entry deleted", "incorrect message flashed")
        self.assertFalse(self.browser.is_element_present_by_text("test entry"), "entry not deleted")
        self.assertFalse(self.browser.is_element_present_by_text("test body"), "entry not deleted")

    # logs in an account associated with the supplied email via appropriate page links
    def login(self, email, password):
        link = self.browser.find_link_by_text("Log in").first
        link.click()
        self.browser.fill("email", email)
        self.browser.fill("password", password)
        btn = self.browser.find_by_value("sign in").first
        btn.click()

    # adds entry with supplied title and body via appropriate page links
    def add_entry(self, title, body):
        link = self.browser.find_link_by_text("Create Post").first
        link.click()
        self.browser.fill("title", title)
        self.browser.fill("body", body)
        btn = self.browser.find_by_value("post").first
        btn.click()

    # edits top entry in blog to supplied title and body
    # assumes top entry owned by logged in user, meant for testing purposes only
    def edit_entry(self, title, body):
        link = self.browser.find_link_by_text("Edit").first
        link.click()
        self.browser.fill("title", title)
        self.browser.fill("body", body)
        btn = self.browser.find_by_value("save").first
        btn.click()

    # views singular entry with given title via appropriate links
    def view_entry(self, title):
        link = self.browser.find_link_by_text(title).first
        link.click()

    # deletes top entry on blog
    # assumes top entry both exists and owned by logged in user, meant for testing purposes only
    def delete_entry(self):
        link = self.browser.find_link_by_text("Delete").first
        link.click()
        btn = self.browser.find_by_value("confirm").first
        btn.click()

    # goes to main page of site
    def visit_site(self):
        self.browser.visit("http://127.0.0.1:8080/")



if __name__ == '__main__':
    unittest.main()
