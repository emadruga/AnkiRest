import json
from datetime import datetime, timedelta
import random
import os

class FlashCard:
    def __init__(self, question, answer, card_id=None):
        self.question = question
        self.answer = answer
        self.card_id = card_id if card_id else random.randint(1000, 9999)
        
        # SM-2 algorithm parameters
        self.repetition = 0
        self.easiness = 2.5
        self.interval = 0
        self.next_review = datetime.now().date()
    
    def to_dict(self):
        return {
            'card_id': self.card_id,
            'question': self.question,
            'answer': self.answer,
            'repetition': self.repetition,
            'easiness': self.easiness,
            'interval': self.interval,
            'next_review': str(self.next_review)
        }
    
    @classmethod
    def from_dict(cls, data):
        card = cls(data['question'], data['answer'], data['card_id'])
        card.repetition = data['repetition']
        card.easiness = data['easiness']
        card.interval = data['interval']
        card.next_review = datetime.strptime(data['next_review'], '%Y-%m-%d').date()
        return card


class SuperMemoSM2:
    def __init__(self, file_path='basketball_flashcards.json'):
        self.file_path = file_path
        self.cards = []
        self.load_cards()
        
        # Create sample basketball flashcards if none exist
        if not self.cards:
            self.create_sample_basketball_cards()
            self.save_cards()
    
    def create_sample_basketball_cards(self):
        """Create 10 sample basketball flashcards if no cards exist."""
        sample_cards = [
            {"question": "What is the height of an NBA basketball hoop?", "answer": "10 feet (3.05 meters)"},
            {"question": "Who holds the NBA record for most points in a single game?", "answer": "Wilt Chamberlain with 100 points (March 2, 1962)"},
            {"question": "What is a triple-double in basketball?", "answer": "When a player accumulates a double-digit number in three of the five statistical categories (points, rebounds, assists, steals, blocks)"},
            {"question": "What is the diameter of a basketball in the NBA?", "answer": "9.43 to 9.51 inches (24-24.2 cm)"},
            {"question": "How long is an NBA basketball game?", "answer": "48 minutes, divided into four 12-minute quarters"},
            {"question": "What is the '3-second rule' in basketball?", "answer": "An offensive player cannot remain in the lane (paint) for more than 3 consecutive seconds"},
            {"question": "Who invented basketball?", "answer": "Dr. James Naismith in December 1891"},
            {"question": "What does 'NBA' stand for?", "answer": "National Basketball Association"},
            {"question": "What is a 'pick and roll' in basketball?", "answer": "An offensive play where a player sets a screen (pick) for a teammate handling the ball and then moves (rolls) toward the basket to receive a pass"},
            {"question": "How many players from each team are on the court during a basketball game?", "answer": "5 players per team"}
        ]
        
        for card_data in sample_cards:
            self.cards.append(FlashCard(card_data["question"], card_data["answer"]))
    
    def load_cards(self):
        """Load flashcards from JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as file:
                    cards_data = json.load(file)
                    self.cards = [FlashCard.from_dict(card) for card in cards_data]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading cards: {e}")
                self.cards = []
    
    def save_cards(self):
        """Save flashcards to JSON file."""
        cards_data = [card.to_dict() for card in self.cards]
        try:
            with open(self.file_path, 'w') as file:
                json.dump(cards_data, file, indent=4)
        except IOError as e:
            print(f"Error saving cards: {e}")
    
    def update_card_with_sm2(self, card, quality):
        """
        Update card using the SuperMemo SM-2 algorithm.
        
        quality is a rating from 0 to 5:
        0 - Complete blackout, wrong answer
        1 - Incorrect response but recognized answer
        2 - Incorrect response but answer remembered after seeing it
        3 - Correct after hesitation
        4 - Correct with effort
        5 - Perfect response
        """
        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5")
        
        # Calculate easiness factor
        card.easiness = max(1.3, card.easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Update repetition count and interval
        if quality < 3:
            # If response was poor, start over
            card.repetition = 0
            card.interval = 0
        else:
            # Increase repetition count and interval
            card.repetition += 1
            
            if card.repetition == 1:
                card.interval = 1
            elif card.repetition == 2:
                card.interval = 6
            else:
                card.interval = round(card.interval * card.easiness)
        
        # Calculate next review date
        if card.interval == 0:
            # Review the same day if failed
            card.next_review = datetime.now().date()
        else:
            card.next_review = datetime.now().date() + timedelta(days=card.interval)
    
    def get_cards_for_review(self):
        """Get all cards that are due for review today."""
        today = datetime.now().date()
        return [card for card in self.cards if card.next_review <= today]
    
    def add_card(self, question, answer):
        """Add a new flashcard."""
        card = FlashCard(question, answer)
        self.cards.append(card)
        self.save_cards()
        return card
    
    def run_review_session(self):
        """Run an interactive review session for cards due today."""
        cards_to_review = self.get_cards_for_review()
        
        if not cards_to_review:
            print("No cards due for review today! Great job keeping up.")
            return
        
        print(f"Starting review session with {len(cards_to_review)} cards...")
        print("For each card, rate your recall from 0-5:")
        print("0: Complete blackout - couldn't remember at all")
        print("1: Incorrect response but recognized the answer")
        print("2: Incorrect response but remembered after seeing the answer")
        print("3: Correct after hesitation")
        print("4: Correct with some effort")
        print("5: Perfect recall")
        print("-" * 50)
        
        for i, card in enumerate(cards_to_review, 1):
            print(f"\nCard {i}/{len(cards_to_review)}")
            print(f"Question: {card.question}")
            input("Press Enter to see the answer...")
            print(f"Answer: {card.answer}")
            
            while True:
                try:
                    quality = int(input("Rate your recall (0-5): "))
                    if 0 <= quality <= 5:
                        break
                    print("Please enter a number between 0 and 5.")
                except ValueError:
                    print("Please enter a valid number.")
            
            self.update_card_with_sm2(card, quality)
            
            # Show next review date
            print(f"Next review: {card.next_review.strftime('%Y-%m-%d')}")
        
        self.save_cards()
        print("\nReview session completed! Your progress has been saved.")
        
        # Show a summary of upcoming reviews
        self.show_upcoming_reviews()
    
    def show_upcoming_reviews(self):
        """Show a summary of upcoming review dates."""
        today = datetime.now().date()
        upcoming_dates = {}
        
        for card in self.cards:
            if card.next_review >= today:
                date_str = card.next_review.strftime('%Y-%m-%d')
                if date_str in upcoming_dates:
                    upcoming_dates[date_str] += 1
                else:
                    upcoming_dates[date_str] = 1
        
        print("\nUpcoming reviews:")
        for date_str, count in sorted(upcoming_dates.items()):
            print(f"{date_str}: {count} cards")


if __name__ == "__main__":
    sm2 = SuperMemoSM2()
    print(f"Loaded {len(sm2.cards)} basketball flashcards")
    
    while True:
        print("\n===== SuperMemo SM-2 Flashcard System =====")
        print("1. Review due cards")
        print("2. Add a new card")
        print("3. Show all cards")
        print("4. Show upcoming reviews")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            sm2.run_review_session()
        elif choice == "2":
            question = input("Enter the question: ")
            answer = input("Enter the answer: ")
            sm2.add_card(question, answer)
            print("Card added successfully!")
        elif choice == "3":
            for i, card in enumerate(sm2.cards, 1):
                print(f"\n{i}. Question: {card.question}")
                print(f"   Answer: {card.answer}")
                print(f"   Next review: {card.next_review}")
        elif choice == "4":
            sm2.show_upcoming_reviews()
        elif choice == "5":
            print("Exiting program. Your progress has been saved.")
            break
        else:
            print("Invalid choice. Please try again.")
