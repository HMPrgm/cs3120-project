from django.test import TestCase
from textbook.models import Textbook, Class
from datetime import date

class TextbookModelTest(TestCase):

    def setUp(self):
        self.test_class = Class.objects.create(department="CS", number="1110", name="Intro to Programming")
        self.test_textbook = Textbook.objects.create(
            title="Python Programming",
            author="John Doe",
            genre="Programming",
            condition="NEW",
            published_date=date(2022, 5, 20),
            associated_class=self.test_class,
            checked_out=False
        )

    def test_textbook_creation(self):
        """Test that a textbook is correctly created."""
        self.assertEqual(self.test_textbook.title, "Python Programming")
        self.assertEqual(self.test_textbook.author, "John Doe")
        self.assertEqual(self.test_textbook.genre, "Programming")
        self.assertEqual(self.test_textbook.condition, "NEW")
        self.assertFalse(self.test_textbook.checked_out)

    def test_textbook_str_method(self):
        self.assertEqual(str(self.test_textbook), "Python Programming by John Doe")

    def test_textbook_associated_class(self):
        self.assertEqual(self.test_textbook.associated_class.name, "Intro to Programming")
        self.assertEqual(str(self.test_textbook.associated_class), "CS 1110")