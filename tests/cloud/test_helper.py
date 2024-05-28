import unittest

from src.helper.helper import extract_schedule_id


class TestHelper(unittest.TestCase):
    def test_extract_schedule_id(self):
        message_text = (
            "123456789.2a83b81d-0c5c-46a4-8607-ac1326ac61b2\ncategory: tpp\nSchedule"
            "news at 12:11:09 (Athens time)\nevery \n0 weeks | 1 days | 0 hours"
        )
        target_id = "123456789.2a83b81d-0c5c-46a4-8607-ac1326ac61b2"
        self.assertEqual(extract_schedule_id(message_text=message_text), target_id)
