import unittest

from app import app, db, Movie, User, forge, initdb


class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        # Update config
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:////:memory:")
        # Create database and table
        db.create_all()
        # Create test data, a user and a movie item
        user = User(name="Test", username="test")
        user.set_password("123")
        movie = Movie(title="Test Movie Title", year="2019")
        # Use add_all() method to add many model in the samethime
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()  # Create test clent
        self.runner = app.test_cli_runner()  # Create test command runner

    def tearDown(self):
        db.session.remove()  # remove database session
        db.drop_all()  # delete database table

    # Test if test app exists
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # Test if test app is in test model
    def test_app_is_testing(self):
        self.assertTrue(app.config["TESTING"])

    # Test 404 page
    def test_404_page(self):
        response = self.client.get("/nothing")
        data = response.get_data(as_text=True)
        self.assertIn("Page Not Found - 404", data)
        self.assertIn("Go Back", data)
        self.assertEqual(response.status_code, 404)

    # Test index page
    def test_index_page(self):
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        self.assertIn("Test's Watchlist", data)
        self.assertIn("Test Movie Title", data)
        self.assertEqual(response.status_code, 200)

    # Auxiliary method to login
    def login(self):
        self.client.post(
            "/login", data=dict(username="test", password="123"), follow_redirects=True
        )

    def test_create_item(self):
        self.login()

        response = self.client.post(
            "/", data=dict(title="New Movie", year="2019"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn("Item created.", data)
        self.assertIn("New Movie", data)

        response = self.client.post(
            "/", data=dict(title="", year="2019"), follow_directs=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("Item created.", data)
        self.assertIn("Invalid input.", data)

        response = self.client.post(
            "/", data=dict(title="New Movie", year=""), follow_directs=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("Item created.", data)
        self.assertIn("Invalid input.", data)

    def test_update_item(self):
        self.login()

        response = self.client.get("/movie/edit/1")
        data = response.get_data(as_text=True)
        self.assertIn("Edit item", data)
        self.assertIn("Test Movie Title", data)
        self.assertIn("2019", data)

        response = self.client.post(
            "/movie/edit/1",
            data=dict(title="New Movie Edited", year="2019"),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertIn("Item updated.", data)
        self.assertIn("New Movie Edited", data)

        response = self.client.post(
            "/movie/edit/1", data=dict(title="", year="2019"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("Item updated.", data)
        self.assertIn("Invalid input.", data)

        response = self.client.post(
            "/movie/edit/1",
            data=dict(title="New Movie Edited Again", year=""),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("Item updated.", data)
        self.assertNotIn("New Movie Edited Again", data)
        self.assertIn("Invalid input.", data)

    def test_delete_item(self):
        self.login()

        response = self.client.post("/movie/delete/1", follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn("Item deleted.", data)
        self.assertNotIn("Test Movie Title", data)

    def test_login_protect(self):
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        self.assertNotIn("Logout", data)
        self.assertNotIn("Settings", data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn("Delete", data)
        self.assertNotIn("Edit", data)

    def test_login(self):
        response = self.client.post(
            "/login", data=dict(username="test", password="123"), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn("Login success.", data)
        self.assertIn("Logout", data)
        self.assertIn("Settings", data)
        self.assertIn("Delete", data)
        self.assertIn("Edit", data)
        self.assertIn('<form method="post">', data)

        response = self.client.post(
            "/login", data=dict(username="test", password="456"), follow_redirects=True
        )
        self.assertNotIn("Login success.", data)
        self.assertIn("Invalid username or password.", data)

        response = self.client.post(
            "/login", data=dict(username="wrong", password="123"), follow_redirects=True
        )
        self.assertNotIn("Login success.", data)
        self.assertIn("Invalid username or password.", data)

        response = self.client.post(
            "/login", data=dict(username="", password="123"), follow_redirects=True
        )
        self.assertNotIn("Login success.", data)
        self.assertIn("Invalid input.", data)

        response = self.client.post(
            "/login", data=dict(username="test", password=""), follow_redirects=True
        )
        self.assertNotIn("Login success.", data)
        self.assertIn("Invalid input.", data)

    def test_logout(self):
        self.login()

        response = self.client.get("/logout", follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn("Goodbye.", data)
        self.assertNotIn("Logout", data)
        self.assertNotIn("Settings", data)
        self.assertNotIn("Delete", data)
        self.assertNotIn("Edit", data)
        self.assertNotIn('<form method="post">', data)

    def test_setting(self):
        self.login()

        response = self.client.get("/settings")
        data = response.get_data(as_text=True)
        self.assertIn("Settings", data)
        self.assertIn("Your Name", data)

        response = self.client.post(
            "/settings",
            data=dict(
                name="Grey Li",
            ),
            follow_directs=True,
        )
        data = response.get_data(as_text=True)
        self.assertIn("Settings updated.", data)
        self.assertIn("Gray Li", data)

        response = self.client.post(
            "/settings",
            data=dict(
                name="",
            ),
            follow_directs=True,
        )
        data = response.get_data(as_text=True)
        self.assertNotIn("Setting updated.", data)
        self.assertIn("Invalid input.", data)

    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn("Done.", result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn("Initialized database.", result.output)

    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(
            args=["admin", "--username", "grey", "--password", "123"]
        )
        self.assertIn("Creating user...", result.output)
        self.assertIn("Done.", result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, "grey")
        self.assertTrue(User.query.first().validate_password("123"))

    def test_admin_command_update(self):
        result = self.runner.invoke(
            args=["admin", "--username", "peter", "--password", "456"]
        )
        self.assertIn("Updating user...", result.output)
        self.assertIn("Done.", result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, "peter")
        self.assertTrue(User.query.first().validate_password("456"))


if __name__ == "__main__":
    unittest.main()
