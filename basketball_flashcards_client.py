import requests
import json


class BasketballFlashcardsClient:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url

    def display_menu(self):
        """Display the main menu options."""
        print("\n--- Basketball Flashcards Menu ---")
        print("1. Review Cards")
        print("2. Add New Card")
        print("3. Show All Cards")
        print("4. Show Upcoming Reviews")
        print("5. Export Database to APKG")
        print("6. Exit")

    def review_cards(self):
        """Initiate card review process."""
        try:
            response = requests.get(f'{self.base_url}/review')
            if response.status_code == 200:
                cards = response.json()
                if not cards:
                    print("No cards available for review.")
                    return

                for card in cards:
                    print("\nFront of Card:")
                    print(card['front'])
                    input("Press Enter to see the back...")
                    print("\nBack of Card:")
                    print(card['back'])

                    while True:
                        difficulty = input("Rate your recall (1-5, where 1 is hardest, 5 is easiest): ")
                        if difficulty in ['1', '2', '3', '4', '5']:
                            break
                        print("Please enter a number between 1 and 5.")

                    # Send review result
                    review_data = {
                        'card_id': card['id'],
                        'difficulty': int(difficulty)
                    }
                    requests.post(f'{self.base_url}/review', json=review_data)
            else:
                print("Failed to retrieve cards for review.")
        except requests.RequestException as e:
            print(f"Error during card review: {e}")

    def add_new_card(self):
        """Add a new flashcard."""
        front = input("Enter the front of the flashcard (question/prompt): ")
        back = input("Enter the back of the flashcard (answer/explanation): ")

        card_data = {
            'front': front,
            'back': back
        }

        try:
            response = requests.post(f'{self.base_url}/cards', json=card_data)
            if response.status_code == 201:
                print("Card added successfully!")
            else:
                print("Failed to add card.")
        except requests.RequestException as e:
            print(f"Error adding card: {e}")

    def show_all_cards(self):
        """Display all flashcards."""
        try:
            response = requests.get(f'{self.base_url}/cards')
            if response.status_code == 200:
                cards = response.json()
                if not cards:
                    print("No cards in the database.")
                    return

                for card in cards:
                    print(f"\nCard ID: {card['id']}")
                    print(f"Front: {card['front']}")
                    print(f"Back: {card['back']}")
            else:
                print("Failed to retrieve cards.")
        except requests.RequestException as e:
            print(f"Error fetching cards: {e}")

    def show_upcoming_reviews(self):
        """Display cards due for review."""
        try:
            response = requests.get(f'{self.base_url}/upcoming')
            if response.status_code == 200:
                cards = response.json()
                if not cards:
                    print("No cards due for review.")
                    return

                for card in cards:
                    print(f"\nCard ID: {card['id']}")
                    print(f"Front: {card['front']}")
                    print(f"Next Review: {card['next_review']}")
            else:
                print("Failed to retrieve upcoming reviews.")
        except requests.RequestException as e:
            print(f"Error fetching upcoming reviews: {e}")

    def export_to_apkg(self):
        """Export database to APKG file."""
        try:
            response = requests.get(f'{self.base_url}/export')
            if response.status_code == 200:
                print("Database exported successfully!")
                # Optionally, you could save the APKG file locally here
            else:
                print("Failed to export database.")
        except requests.RequestException as e:
            print(f"Error exporting database: {e}")

    def run(self):
        """Main client application loop."""
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-6): ")

            if choice == '1':
                self.review_cards()
            elif choice == '2':
                self.add_new_card()
            elif choice == '3':
                self.show_all_cards()
            elif choice == '4':
                self.show_upcoming_reviews()
            elif choice == '5':
                self.export_to_apkg()
            elif choice == '6':
                print("Exiting Basketball Flashcards. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


def main():
    client = BasketballFlashcardsClient()
    client.run()


if __name__ == '__main__':
    main()