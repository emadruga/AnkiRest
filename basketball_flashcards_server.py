import os
import sqlite3
import json
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from anki.collection import Collection
from anki.exporting import AnkiPackageExporter

app = Flask(__name__)

# Database initialization
DATABASE = 'basketball_flashcards.db'


def get_db():
    """Establish database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize the database schema."""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                due_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                ease_factor REAL DEFAULT 2.5,
                interval INTEGER DEFAULT 1,
                repetitions INTEGER DEFAULT 0
            )
        ''')

        # Anki-style collection table
        db.execute('''
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

        # Empty graves table (as specified)
        db.execute('''
            CREATE TABLE IF NOT EXISTS graves (
                usn INTEGER,
                oid INTEGER,
                type INTEGER
            )
        ''')

        # Insert a default configuration if not exists
        db.execute('''
            INSERT OR IGNORE INTO col 
            (id, crt, mod, scm, ver, dty, usn, ls, 
             conf, models, decks, dconf, tags) 
            VALUES (
                1, 
                strftime('%s', 'now'), 
                strftime('%s', 'now'), 
                0, 
                11, 
                0, 
                0, 
                0, 
                '{}', 
                '{}', 
                '{}', 
                '{}', 
                '{}'
            )
        ''')
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection at end of request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def calculate_next_review(card, difficulty):
    """
    Implement SuperMemo-2 algorithm for spaced repetition.
    Args:
        card: Current card details
        difficulty: User's recall difficulty (1-5)
    Returns:
        next review date, new interval, new ease factor
    """
    if difficulty < 3:  # Reset if difficult
        interval = 1
        repetitions = 0
        ease_factor = max(1.3, card['ease_factor'] - 0.2)
    else:
        if card['repetitions'] == 0:
            interval = 1
        elif card['repetitions'] == 1:
            interval = 6
        else:
            interval = round(card['interval'] * card['ease_factor'])

        repetitions = card['repetitions'] + 1
        ease_factor = card['ease_factor'] + (0.1 - (5 - difficulty) * (0.08 + (5 - difficulty) * 0.02))
        ease_factor = max(1.3, ease_factor)

    next_review = datetime.now() + timedelta(days=interval)

    return next_review, interval, ease_factor


@app.route('/review', methods=['GET'])
def get_review_cards():
    """Get 10 random cards due for review."""
    db = get_db()
    now = datetime.now()

    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM cards 
        WHERE due_date <= ? 
        ORDER BY RANDOM() 
        LIMIT 10
    ''', (now.strftime('%Y-%m-%d %H:%M:%S'),))

    cards = [dict(row) for row in cursor.fetchall()]
    return jsonify(cards)


@app.route('/review', methods=['POST'])
def process_review():
    """Process card review and update its spaced repetition parameters."""
    db = get_db()
    review_data = request.json

    cursor = db.cursor()
    cursor.execute('SELECT * FROM cards WHERE id = ?', (review_data['card_id'],))
    card = cursor.fetchone()

    if card:
        card_dict = dict(card)
        next_review, interval, ease_factor = calculate_next_review(
            card_dict,
            review_data['difficulty']
        )

        cursor.execute('''
            UPDATE cards 
            SET due_date = ?, 
                interval = ?, 
                ease_factor = ?, 
                repetitions = repetitions + 1 
            WHERE id = ?
        ''', (
            next_review.strftime('%Y-%m-%d %H:%M:%S'),
            interval,
            ease_factor,
            review_data['card_id']
        ))
        db.commit()
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "card not found"}), 404


@app.route('/cards', methods=['GET'])
def get_all_cards():
    """Retrieve all flashcards."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM cards')
    cards = [dict(row) for row in cursor.fetchall()]
    return jsonify(cards)


@app.route('/cards', methods=['POST'])
def add_card():
    """Add a new flashcard."""
    db = get_db()
    card_data = request.json

    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO cards (front, back, due_date) 
        VALUES (?, ?, ?)
    ''', (
        card_data['front'],
        card_data['back'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    db.commit()
    return jsonify({"id": cursor.lastrowid}), 201


@app.route('/upcoming', methods=['GET'])
def get_upcoming_reviews():
    """Get cards upcoming for review."""
    db = get_db()
    now = datetime.now()

    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM cards 
        WHERE due_date > ? 
        ORDER BY due_date
    ''', (now.strftime('%Y-%m-%d %H:%M:%S'),))

    cards = [dict(row) for row in cursor.fetchall()]
    return jsonify(cards)


@app.route('/export', methods=['GET'])
def export_to_apkg():
    """Export database to Anki Package."""
    # Create a temporary Anki collection
    apkg_filename = 'basketball_flashcards.apkg'

    # Create a temporary Anki collection
    col = Collection('temp.anki2')

    # Fetch all cards from SQLite
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM cards')
    cards = cursor.fetchall()

    # Create a basic model
    model = col.models.new('Basketball Flashcards')
    model['type'] = 1  # 0=standard, 1=cloze

    # Add front/back fields
    front_field = col.models.new_field('Front')
    back_field = col.models.new_field('Back')
    col.models.addField(model, front_field)
    col.models.addField(model, back_field)

    # Create a deck
    did = col.decks.id('Basketball Flashcards')
    col.decks.select(did)

    # Add cards to the collection
    for card_data in cards:
        note = col.newNote()
        note.note_type()['did'] = did
        note['Front'] = card_data['front']
        note['Back'] = card_data['back']
        col.addNote(note)

    # Export to APKG
    exporter = AnkiPackageExporter(col)
    exporter.exportInto(apkg_filename)

    # Close the temporary collection
    col.close()

    return jsonify({"status": "exported", "filename": apkg_filename}), 200


def main():
    """Initialize database and run Flask server."""
    init_db()
    app.run(port=8000,debug=True)
    CORS(app, origins="*")


if __name__ == '__main__':
    main()