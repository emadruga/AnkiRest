import os
import sys
import json
import unittest
import tempfile
import requests


class BasketballFlashcardsAPITest(unittest.TestCase):
    BASE_URL = 'http://localhost:8000'

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_card = {
            'front': 'Who is considered the GOAT in basketball?',
            'back': 'Michael Jordan is widely considered the Greatest of All Time (GOAT)'
        }

    def test_1_add_card(self):
        """Test adding a new card to the database."""
        response = requests.post(f'{self.BASE_URL}/cards', json=self.test_card)
        self.assertEqual(response.status_code, 201)

        # Store the card ID for future tests
        self.__class__.added_card_id = response.json()['id']

    def test_2_get_all_cards(self):
        """Test retrieving all cards."""
        response = requests.get(f'{self.BASE_URL}/cards')
        self.assertEqual(response.status_code, 200)

        cards = response.json()
        self.assertTrue(len(cards) > 0)

        # Check if the recently added card exists
        added_card_found = any(
            card['front'] == self.test_card['front'] and
            card['back'] == self.test_card['back']
            for card in cards
        )
        self.assertTrue(added_card_found)

    def test_3_review_cards(self):
        """Test retrieving cards for review and processing a review."""
        # First, get review cards
        review_response = requests.get(f'{self.BASE_URL}/review')
        self.assertEqual(review_response.status_code, 200)

        review_cards = review_response.json()

        # If cards are available, process a review
        if review_cards:
            review_data = {
                'card_id': review_cards[0]['id'],
                'difficulty': 4  # Easy recall
            }
            review_process_response = requests.post(f'{self.BASE_URL}/review', json=review_data)
            self.assertEqual(review_process_response.status_code, 200)

    def test_4_upcoming_reviews(self):
        """Test retrieving upcoming reviews."""
        response = requests.get(f'{self.BASE_URL}/upcoming')
        self.assertEqual(response.status_code, 200)

        upcoming_cards = response.json()
        # Note: upcoming cards might be empty depending on review status
        self.assertIsInstance(upcoming_cards, list)

    def test_5_export_to_apkg(self):
        """Test exporting database to APKG."""
        response = requests.get(f'{self.BASE_URL}/export')
        self.assertEqual(response.status_code, 200)

        export_data = response.json()
        self.assertEqual(export_data['status'], 'exported')
        self.assertTrue(export_data['filename'].endswith('.apkg'))

        # Verify the file was created (optional)
        self.assertTrue(os.path.exists(export_data['filename']))


def run_tests():
    """Run the test suite."""
    print("Running Basketball Flashcards API Tests...")
    unittest.main(argv=[''], exit=False)


if __name__ == '__main__':
    run_tests()
