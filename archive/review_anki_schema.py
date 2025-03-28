import sqlite3
import time
import random
import os
from datetime import datetime, timedelta

class AnkiSM2:
    def __init__(self, db_path='basketball_anki.db'):
        """
        Initialize the Anki-compatible SuperMemo SM-2 system with SQLite.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Connect to database
        self.connect()
        
        # Create tables if they don't exist
        self.create_tables()
        
        # Check if cards exist, otherwise create sample cards
        self.cursor.execute("SELECT COUNT(*) FROM notes")
        if self.cursor.fetchone()[0] == 0:
            self.create_sample_basketball_cards()
    
    def connect(self):
        """Establish connection to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create the necessary tables mimicking Anki's schema."""
        # Create the col (collection) table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS col (
            id INTEGER PRIMARY KEY,
            crt INTEGER,
            mod INTEGER,
            scm INTEGER,
            ver INTEGER,
            dty INTEGER,
            usn INTEGER,
            ls INTEGER,
            conf TEXT,
            models TEXT,
            decks TEXT,
            dconf TEXT,
            tags TEXT
        )
        ''')
        
        # Create the notes table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            guid TEXT,
            mid INTEGER,
            mod INTEGER,
            usn INTEGER,
            tags TEXT,
            flds TEXT,
            sfld TEXT,
            csum INTEGER,
            flags INTEGER,
            data TEXT
        )
        ''')
        
        # Create the cards table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY,
            nid INTEGER,
            did INTEGER,
            ord INTEGER,
            mod INTEGER,
            usn INTEGER,
            type INTEGER,
            queue INTEGER,
            due INTEGER,
            ivl INTEGER,
            factor INTEGER,
            reps INTEGER,
            lapses INTEGER,
            left INTEGER,
            odue INTEGER,
            odid INTEGER,
            flags INTEGER,
            data TEXT,
            FOREIGN KEY(nid) REFERENCES notes(id)
        )
        ''')
        
        # Create the revlog table (review history)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS revlog (
            id INTEGER PRIMARY KEY,
            cid INTEGER,
            usn INTEGER,
            ease INTEGER,
            ivl INTEGER,
            lastIvl INTEGER,
            factor INTEGER,
            time INTEGER,
            type INTEGER,
            FOREIGN KEY(cid) REFERENCES cards(id)
        )
        ''')
        
        # Check if collection record exists, if not create it
        self.cursor.execute("SELECT COUNT(*) FROM col")
        if self.cursor.fetchone()[0] == 0:
            # Insert default collection record
            current_time = int(time.time())
            self.cursor.execute(
                "INSERT INTO col VALUES (1, ?, ?, 1, 11, 0, 0, 0, '{}', '{}', '{}', '{}', '{}')",
                (current_time, current_time)
            )
        
        self.conn.commit()
    
    def create_sample_basketball_cards(self):
        """Create 10 sample basketball flashcards in the database."""
        # Create a default model (note type)
        model_id = int(time.time() * 1000)
        
        # Create a default deck
        deck_id = 1
        
        # Sample basketball flashcards
        basketball_cards = [
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
        
        current_time = int(time.time())
        
        for card_data in basketball_cards:
            # Generate a unique ID for the note based on timestamp
            note_id = int(time.time() * 1000) + random.randint(1, 1000)
            time.sleep(0.001)  # Ensure unique IDs
            
            # Create the note (question + answer)
            fields = card_data["question"] + "\x1f" + card_data["answer"]  # \x1f is the field separator in Anki
            
            # Calculate sfld (sort field) and csum (checksum)
            sfld = card_data["question"]
            csum = self.calculate_checksum(sfld)
            
            # Insert the note
            self.cursor.execute('''
            INSERT INTO notes 
            (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                note_id,
                str(note_id),  # guid
                model_id,  # model id
                current_time,  # modification time
                -1,  # usn (update sequence number)
                "",  # tags
                fields,  # fields
                sfld,  # sort field
                csum,  # checksum
                0,  # flags
                ""  # data
            ))
            
            # Create a card linked to this note
            card_id = note_id  # Use same ID for simplicity
            
            # Insert the card with initial SM-2 values
            self.cursor.execute('''
            INSERT INTO cards 
            (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                card_id,
                note_id,  # note id
                deck_id,  # deck id
                0,  # ord (card template)
                current_time,  # modification time
                -1,  # usn
                0,  # type (0=new, 1=learning, 2=due, 3=filtered)
                0,  # queue (0=new, 1=learning, 2=due)
                random.randint(1, 10),  # due position for new cards
                0,  # interval
                2500,  # factor (ease factor * 1000)
                0,  # reps
                0,  # lapses
                0,  # left
                0,  # original due
                0,  # original deck id
                0,  # flags
                ""  # data
            ))
        
        self.conn.commit()
    
    def calculate_checksum(self, text):
        """Calculate a simple checksum for the sort field."""
        # In Anki, this is a more complex function, but this is a simplified version
        return sum(ord(c) for c in text) & 0xFFFFFFFF
    
    def get_cards_due_today(self):
        """Get all cards that are due for review today."""
        # Get current day (days since Unix epoch)
        today = self.days_since_epoch(datetime.now())
        
        # Get new cards (queue=0) and cards due today or earlier (queue=2, due <= today)
        self.cursor.execute('''
        SELECT c.id, n.flds 
        FROM cards c 
        JOIN notes n ON c.nid = n.id 
        WHERE (c.queue = 0) OR (c.queue = 2 AND c.due <= ?)
        ''', (today,))
        
        due_cards = self.cursor.fetchall()
        result = []
        
        for card_id, fields in due_cards:
            # Split fields by the separator
            parts = fields.split("\x1f")
            if len(parts) >= 2:
                result.append({
                    'id': card_id,
                    'question': parts[0],
                    'answer': parts[1]
                })
        
        return result
    
    def days_since_epoch(self, date):
        """Convert a datetime to days since Unix epoch (Anki's due date format)."""
        epoch = datetime(1970, 1, 1)
        return (date - epoch).days
    
    def date_from_days(self, days):
        """Convert days since epoch to a datetime object."""
        epoch = datetime(1970, 1, 1)
        return epoch + timedelta(days=days)
    
    def apply_sm2_algorithm(self, card_id, quality):
        """
        Apply the SuperMemo SM-2 algorithm to update a card's review schedule.
        
        Args:
            card_id: ID of the card to update
            quality: Quality of recall (0-5)
        """
        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5")
        
        # Get current card info
        self.cursor.execute('''
        SELECT type, queue, ivl, factor, reps, lapses, left
        FROM cards WHERE id = ?
        ''', (card_id,))
        
        card = self.cursor.fetchone()
        if not card:
            raise ValueError(f"No card found with ID {card_id}")
        
        type_val, queue, interval, factor, reps, lapses, left = card
        
        # Current timestamp
        current_time = int(time.time())
        
        # Today in days since epoch
        today = self.days_since_epoch(datetime.now())
        
        # Convert ease factor from Anki's format (multiplied by 1000)
        ease_factor = factor / 1000.0
        
        # Apply SM-2 algorithm
        if quality < 3:
            # Failed recall - card goes back to learning
            new_interval = 1
            new_ease_factor = max(1.3, ease_factor - 0.2)
            new_type = 1  # learning
            new_queue = 1  # learning
            due = current_time + (new_interval * 60)  # Due in n minutes from now
            lapses += 1
            left = 3  # Start with 3 steps in learning
        else:
            # Successful recall
            reps += 1
            
            # Update ease factor
            new_ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
            
            # Calculate new interval
            if interval == 0:
                # First successful review
                new_interval = 1
            elif interval == 1:
                # Second successful review
                new_interval = 6
            else:
                # Subsequent reviews
                new_interval = int(interval * new_ease_factor)
            
            new_type = 2  # review
            new_queue = 2  # review
            due = today + new_interval  # Due in n days
            left = 0
        
        # Update the card in the database
        self.cursor.execute('''
        UPDATE cards
        SET type = ?, queue = ?, due = ?, ivl = ?, factor = ?, reps = ?, lapses = ?, left = ?, mod = ?
        WHERE id = ?
        ''', (
            new_type,
            new_queue,
            due,
            new_interval,
            int(new_ease_factor * 1000),  # Convert back to Anki's format
            reps,
            lapses,
            left,
            current_time,
            card_id
        ))
        
        # Add an entry to the review log
        review_id = int(time.time() * 1000)  # Timestamp in milliseconds
        
        self.cursor.execute('''
        INSERT INTO revlog
        (id, cid, usn, ease, ivl, lastIvl, factor, time, type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            review_id,
            card_id,
            -1,  # usn
            quality + 1,  # Anki uses 1-4 instead of 0-3 for the ease
            new_interval,
            interval,
            int(new_ease_factor * 1000),
            random.randint(3000, 15000),  # Time spent in milliseconds (simulated)
            0 if quality < 3 else 1  # 0=fail, 1=pass
        ))
        
        self.conn.commit()
        
        # Return the next review date for display
        if new_queue == 1:  # learning
            minutes = new_interval
            return f"Next review: in {minutes} minute(s)"
        else:  # review
            next_review_date = self.date_from_days(due)
            return f"Next review: {next_review_date.strftime('%Y-%m-%d')}"
    
    def add_card(self, question, answer):
        """Add a new flashcard to the database."""
        current_time = int(time.time())
        
        # Generate IDs
        note_id = int(time.time() * 1000) + random.randint(1, 1000)
        card_id = note_id
        
        # Create the note fields
        fields = question + "\x1f" + answer
        sfld = question
        csum = self.calculate_checksum(sfld)
        
        # Insert the note
        self.cursor.execute('''
        INSERT INTO notes 
        (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            note_id,
            str(note_id),  # guid
            1,  # model id (fixed for simplicity)
            current_time,  # modification time
            -1,  # usn
            "",  # tags
            fields,  # fields
            sfld,  # sort field
            csum,  # checksum
            0,  # flags
            ""  # data
        ))
        
        # Insert the card
        self.cursor.execute('''
        INSERT INTO cards 
        (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            card_id,
            note_id,  # note id
            1,  # deck id
            0,  # ord
            current_time,  # modification time
            -1,  # usn
            0,  # type (new)
            0,  # queue (new)
            random.randint(1, 10),  # due position for new cards
            0,  # interval
            2500,  # factor (2.5 * 1000)
            0,  # reps
            0,  # lapses
            0,  # left
            0,  # original due
            0,  # original deck id
            0,  # flags
            ""  # data
        ))
        
        self.conn.commit()
        return card_id
    
    def get_all_cards(self):
        """Get all cards with their review information."""
        self.cursor.execute('''
        SELECT c.id, n.flds, c.type, c.queue, c.due, c.ivl, c.factor, c.reps, c.lapses
        FROM cards c
        JOIN notes n ON c.nid = n.id
        ORDER BY c.nid
        ''')
        
        all_cards = self.cursor.fetchall()
        result = []
        
        for card_id, fields, type_val, queue, due, interval, factor, reps, lapses in all_cards:
            parts = fields.split("\x1f")
            
            # Calculate next review date
            if queue == 2:  # review queue
                next_review = self.date_from_days(due).strftime('%Y-%m-%d')
            elif queue == 1:  # learning queue
                next_review = "Learning"
            else:  # new queue
                next_review = "New"
            
            result.append({
                'id': card_id,
                'question': parts[0],
                'answer': parts[1],
                'next_review': next_review,
                'ease_factor': factor / 1000.0,
                'reviews': reps,
                'lapses': lapses
            })
        
        return result
    
    def get_upcoming_reviews(self, days=30):
        """Get a summary of upcoming reviews."""
        today = self.days_since_epoch(datetime.now())
        end_day = today + days
        
        # Get cards that are scheduled for review in the next 'days' days
        self.cursor.execute('''
        SELECT due, COUNT(*)
        FROM cards
        WHERE queue = 2 AND due BETWEEN ? AND ?
        GROUP BY due
        ORDER BY due
        ''', (today, end_day))
        
        upcoming = self.cursor.fetchall()
        result = {}
        
        for due_day, count in upcoming:
            date_str = self.date_from_days(due_day).strftime('%Y-%m-%d')
            result[date_str] = count
        
        return result
    
    def run_review_session(self):
        """Run an interactive flashcard review session."""
        cards = self.get_cards_due_today()
        
        if not cards:
            print("No cards due for review today! Great job keeping up.")
            return
        
        print(f"Starting review session with {len(cards)} cards...")
        print("For each card, rate your recall from 0-5:")
        print("0: Complete blackout - couldn't remember at all")
        print("1: Incorrect response but recognized the answer")
        print("2: Incorrect response but remembered after seeing the answer")
        print("3: Correct after hesitation")
        print("4: Correct with some effort")
        print("5: Perfect recall")
        print("-" * 50)
        
        for i, card in enumerate(cards, 1):
            print(f"\nCard {i}/{len(cards)}")
            print(f"Question: {card['question']}")
            input("Press Enter to see the answer...")
            print(f"Answer: {card['answer']}")
            
            while True:
                try:
                    quality = int(input("Rate your recall (0-5): "))
                    if 0 <= quality <= 5:
                        break
                    print("Please enter a number between 0 and 5.")
                except ValueError:
                    print("Please enter a valid number.")
            
            next_review = self.apply_sm2_algorithm(card['id'], quality)
            print(next_review)
        
        print("\nReview session completed! Your progress has been saved.")

def main():
    sm2 = AnkiSM2()
    
    while True:
        print("\n===== Anki-Compatible SuperMemo SM-2 System =====")
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
            card_id = sm2.add_card(question, answer)
            print(f"Card added successfully with ID: {card_id}")
        elif choice == "3":
            cards = sm2.get_all_cards()
            for i, card in enumerate(cards, 1):
                print(f"\n{i}. Question: {card['question']}")
                print(f"   Answer: {card['answer']}")
                print(f"   Next review: {card['next_review']}")
                print(f"   Ease factor: {card['ease_factor']:.2f}")
                print(f"   Reviews: {card['reviews']}, Lapses: {card['lapses']}")
        elif choice == "4":
            upcoming = sm2.get_upcoming_reviews()
            print("\nUpcoming reviews:")
            for date_str, count in sorted(upcoming.items()):
                print(f"{date_str}: {count} cards")
        elif choice == "5":
            sm2.close()
            print("Exiting program. Your progress has been saved.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
