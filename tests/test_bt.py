"""
test_bt.py - Unit testing for the ALC Breach Tool.
Run with: python -m unittest tests/test_bt.py -v
"""

from __future__ import annotations
import csv, sys, tempfile, unittest
from pathlib import Path
import requests as req
from unittest.mock import MagicMock, patch
from src.breach_checker import BreachChecker, BreachResult, SummaryStats, is_valid_email
from src.io_handler import read_email_csv, write_results_csv
from src.example import ExampleBreachClient
from src.api_client import IntelligenceXClient, APIError

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))

class TestEmailValidation(unittest.TestCase):
    VALID = ["neil@example.com", "jane@test.co.uk", "fiona@company.net", "n+dj@met.uk"]
    INVALID = ["", "email", "test@", "test.com", "test@.com", "test@@hotmail.com", "@test.org"]

    def test_valid_emails(self):
        for e in self.VALID:
            with self.subTest(email=0): 
                self.assertTrue(is_valid_email(e))
    
    def test_invalid_emails(self):
        for e in self.INVALID:
            with self.subTest(email=0): 
                self.assertFalse(is_valid_email(e))

class TestReadEmailCsv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    
    def test_read_standard_column(self):
        f = self.p/"e.csv"; f.write_text("email\nread@test.com\n")
        self.assertEqual(read_email_csv(f), ["read@test.com"])

    def test_skips_blank_rows(self):
        f = self.p/"e.csv"; f.write_text("email\na@test.com\n\nc@test.com\n")
        self.assertEqual(len(read_email_csv(f)),2)
    
    def test_raises_on_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_email_csv("/no/file.csv")
    
    def test_raises_on_empty_file(self):
        f = self.p/"e.csv"; f.write_text("")
        with self.assertRaises(ValueError): read_email_csv(f)

class TestWriteResultsCsv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    
    def test_writes_correct_columns(self):
        out = self.p/"o.csv"
        write_results_csv([BreachResult("a@b.com", True,["src"])], out)
        rows = list(csv.DictReader(out.open()))
        self.assertEqual(rows[0]["breached"], "True")
        self.assertEqual(rows[0]["site_where_breached"], "src")

    def test_semicolon_separated_sources(self):
        out = self.p/"o.csv"
        write_results_csv([BreachResult("u@test.com", True, ["a", "b", "c"])], out)
        row = list(csv.DictReader(out.open()))[0]
        self.assertEqual(row["site_where_breached"], "a;b;c")

class TestBreachCheckerHappyPath(unittest.TestCase):
    def setUp(self):
        self.checker = BreachChecker(api_client=ExampleBreachClient(), request_delay=0)
    
    def test_known_breached_email(self):
        results, stats = self.checker.check_emails(["neil@example.com"])
        self.assertTrue(results[0].breached)
        self.assertIn("facebook.com-2025", results[0].breach_sources)
    
    def test_known_clean_email(self):
        results, stats = self.checker.check_emails(["test@safeemail.net"])
        self.assertFalse(results[0].breached)
        
    def test_invalid_email_flagged(self):
        results, stats = self.checker.check_emails(["not-an-email"])
        self.assertEqual(results[0].breach_sources, ["INVALID_EMAIL"])
        self.assertEqual(stats.total_invalid, 1)
    
    def test_empty_input(self):
        results, stats = self.checker.check_emails([])
        self.assertEqual(results, [])

class TestBreachCheckerErrors(unittest.TestCase):
    def test_api_error_returns_sentinel(self):
        c = ExampleBreachClient(simulate_error_for={"fail@example.com"})
        results, _ = BreachChecker(api_client=c, request_delay=0).check_emails(["fail@example.com"])
        self.assertEqual(results[0].breach_sources, ["CHECK_ERROR"])
    
    def test_partial_failure_continues(self):
        c = ExampleBreachClient(simulate_error_for={"fail@example.com"})
        results, _ = BreachChecker(api_client=c, request_delay=0).check_emails(["fail@example.com", "neil@example.com"])
        self.assertEqual(len(results), 2)
        self.assertTrue(results[1].breached)

class TestSummaryStats(unittest.TestCase):
    def test_breach_rate(self):
        s = SummaryStats(total_checked=10, total_breached=3, total_clean=7)
        self.assertAlmostEqual(s.breach_rate, 30.0, places=1)

    def test_zero_division(self):
        self.assertEqual(SummaryStats(total_checked=0).breach_rate, 0.0)
    
    def test_top_sources(self):
        s = SummaryStats(source_counts={"a":5, "b":10,"c":3})
        self.assertEqual(s.top_sources(2)[0], ("b",10))

class TestAPIClientRetry(unittest.TestCase):
    def test_429_triggers_retry(self):
        c = IntelligenceXClient(api_key="k", max_retries=3, backoff_factor=0.01)
        r429 = MagicMock(status_code=429)
        r200 = MagicMock(status_code=200); r200.json.return_value={"id":"abd"}
        rres = MagicMock(status_code=200)
        rres.json.return_value={"selectors":
                                [{"selectorvalue":"b.example.com"}]}
        with patch.object(c._session,"request",side_effect=[r429, r200, rres]), patch("time.sleep"):
            self.assertEqual(c.search_email("u@t.com"), ["b.example.com"])
    
    def test_auth_error_raises(self):
        c = IntelligenceXClient(api_key="bad", backoff_factor=0.01)
        with patch.object(c._session,"request",return_value=MagicMock(status_code=403)):
            with self.assertRaises(APIError):
                c.search_email("u@t.com")
    
    def test_timeout_returns_none(self):
        c = IntelligenceXClient(api_key="k",max_retries=2,backoff_factor=0.01)
        with patch.object(c._session,"request",side_effect=req.exceptions.Timeout), patch("time.sleep"):
            self.assertIsNone(c._request("GET", "https://facebook.com",cid="t"))

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()

    def test_full_pipeline(self):
        inp = self.p/"i.csv"
        inp.write_text("email\nneil@example.com\njane@test.co.uk\nnotvalid\n")
        out = self.p/"o.csv"
        emails = read_email_csv(inp)
        results, stats = BreachChecker(
            api_client=ExampleBreachClient(), request_delay=0).check_emails(emails)
        write_results_csv(results, out)
        rows = list(csv.DictReader(out.open()))
        self.assertEqual(len(rows), 3)
        self.assertEqual(stats.total_breached, 1)
        self.assertEqual(stats.total_clean, 1)
        self.assertEqual(stats.total_invalid, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
