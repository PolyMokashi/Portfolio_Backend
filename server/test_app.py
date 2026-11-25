import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import initialize_database, main, read_portfolio


class PortfolioDatabaseTests(unittest.TestCase):
    def test_binds_to_all_interfaces_when_platform_port_is_set(self):
        with patch.dict(os.environ, {"PORT": "10000"}, clear=True):
            with patch("app.initialize_database"):
                with patch("app.ThreadingHTTPServer") as server_class:
                    main()

        self.assertEqual(server_class.call_args.args[0], ("0.0.0.0", 10000))

    def test_initializes_all_portfolio_sections(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            db_path = Path(temporary_directory) / "portfolio.sqlite3"
            initialize_database(db_path)

            portfolio = read_portfolio(db_path)

            self.assertEqual(
                set(portfolio),
                {
                    "profile",
                    "projects",
                    "certificates",
                    "education",
                    "experience",
                    "footerLinks",
                    "skills",
                },
            )
            self.assertEqual(len(portfolio["projects"]), 9)
            self.assertEqual(len(portfolio["certificates"]), 7)
            self.assertEqual(len(portfolio["skills"]), 40)
            self.assertEqual(len(portfolio["footerLinks"]), 5)
            self.assertTrue(
                any(
                    ".m3u8" in project.get("src", "")
                    for project in portfolio["projects"]
                )
            )
            self.assertTrue(portfolio["profile"]["image"].startswith("/media/"))
            self.assertTrue(portfolio["profile"]["summary"])
            self.assertEqual(
                portfolio["profile"]["languages"],
                [
                    {"name": "English", "level": "C1"},
                    {"name": "German", "level": "A2"},
                ],
            )
            project_titles = {project["Title"] for project in portfolio["projects"]}
            self.assertTrue(
                {
                    "Gyanova v4: Autonomous Multi-Agent System",
                    "EduVid AI",
                    "PolyVault",
                }.issubset(project_titles)
            )
            self.assertTrue(
                {"Leaf Disease Detection", "Wine Quality Clustering"}.isdisjoint(
                    project_titles
                )
            )

    def test_existing_database_content_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            db_path = Path(temporary_directory) / "portfolio.sqlite3"
            initialize_database(db_path)

            import sqlite3

            with sqlite3.connect(db_path) as connection:
                connection.execute(
                    "UPDATE portfolio_sections SET content = ? WHERE name = 'profile'",
                    (json.dumps({"name": "Updated"}),),
                )

            initialize_database(db_path)

            self.assertEqual(read_portfolio(db_path)["profile"]["name"], "Updated")


if __name__ == "__main__":
    unittest.main()
