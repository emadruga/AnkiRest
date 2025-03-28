import pprint
import sqlite3
import json
import os
import time
import random
import zipfile
import shutil
import tempfile


class AnkiFlashcardApp:
    def __init__(self, db_path=None):
        """Initialize the flashcard app with a database path."""
        self.db_path = db_path or "collection.anki2"
        self.conn = None
        self.media_files = []

    def connect(self):
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def initialize_database(self):
        """Initialize a new database with the correct Anki schema."""
        self.connect()
        cursor = self.conn.cursor()

        # Create the 'col' table (collection table)
        cursor.execute('''
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

        # Create the 'notes' table
        cursor.execute('''
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

        # Create the 'cards' table
        cursor.execute('''
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
            data TEXT
        )
        ''')

        # Create graves table for tracking deletions
        cursor.execute('''
         CREATE TABLE IF NOT EXISTS graves (
             usn INTEGER NOT NULL,
             oid INTEGER NOT NULL,
             type INTEGER NOT NULL
         )
         ''')

        # Create the 'revlog' table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS revlog (
            id INTEGER PRIMARY KEY,
            cid INTEGER,
            usn INTEGER,
            ease INTEGER,
            ivl INTEGER,
            lastIvl INTEGER,
            factor INTEGER,
            time INTEGER,
            type INTEGER
        )
        ''')

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_notes_usn ON notes (usn)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_cards_usn ON cards (usn)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_revlog_usn ON revlog (usn)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_cards_nid ON cards (nid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_cards_sched ON cards (did, queue, due)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_revlog_cid ON revlog (cid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_notes_csum ON notes (csum)")

        # Initialize the collection with default values
        current_time = int(time.time())

        # Basic model for simple flashcards
        basic_model = self._create_basic_model()
        default_deck = self._create_default_deck()

        # Create the conf JSON
        conf = {
            "nextTags": [],
            "sortBackwards": False,
            "addToCur": True,
            "curDeck": 1,
            "newBury": True,
            "newSpread": 0,
            "dueCounts": True,
            "curModel": 1,
            "estTimes": True,
            "collapseTime": 1200,
            "timeLim": 0,
            "activeDecks": [1],
            "dayLearnFirst": False,
            "timeoutAnswer": False
        }

        # Create default deck configuration
        deck_conf = {
            "1": {
                "id": 1,
                "name": "Default",
                "replayq": True,
                "lapse": {
                    "leechFails": 8,
                    "delays": [10],
                    "minInt": 1,
                    "leechAction": 0,
                    "mult": 0
                },
                "rev": {
                    "bury": True,
                    "ivlFct": 1,
                    "ease4": 1.3,
                    "maxIvl": 36500,
                    "perDay": 200,
                    "minSpace": 1,
                    "fuzz": 0.05
                },
                "timer": 0,
                "maxTaken": 60,
                "usn": 0,
                "new": {
                    "bury": True,
                    "separate": True,
                    "delays": [1, 10],
                    "initialFactor": 2500,
                    "ints": [1, 4, 7],
                    "order": 1,
                    "perDay": 20
                },
                "mod": current_time,
                "autoplay": True
            }
        }
        # Check if collection record exists, if not create it
        cursor.execute("SELECT COUNT(*) FROM col")
        if cursor.fetchone()[0] == 0:
            # Initialize the collection with the models, decks, and configuration
            cursor.execute('''
            INSERT INTO col (id, crt, mod, scm, ver, dty, usn, ls, conf, models, decks, dconf, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                1,  # id
                current_time,  # crt - creation time
                current_time,  # mod - modification time
                current_time * 1000,  # scm - schema modification time
                11,  # ver - version
                0,  # dty - dirty?
                0,  # usn - update sequence number
                0,  # ls - last sync time
                json.dumps(conf),  # conf - configuration
                json.dumps({basic_model["id"]: basic_model}),  # models
                json.dumps(default_deck),  # decks
                json.dumps(deck_conf),  # dconf - deck configuration
                json.dumps({})  # tags
            ))

        self.conn.commit()

    def _create_basic_model(self):
        """Create a basic model for flashcards."""
        model_id = int(time.time() * 1000)  # Use timestamp as ID

        model = {
            "id": model_id,
            "name": "Basic",
            "type": 0,
            "mod": int(time.time()),
            "usn": 0,
            "sortf": 0,  # Sort by first field
            "tags": [],
            "did": 1,  # Default deck ID
            "tmpls": [  # Templates
                {
                    "name": "Card 1",
                    "ord": 0,
                    "qfmt": "{{Front}}",
                    "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
                    "bqfmt": "",
                    "bafmt": "",
                    "did": None,
                    "bfont": "",
                    "bsize": 0
                }
            ],
            "flds": [  # Fields
                {
                    "name": "Front",
                    "ord": 0,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "media": []
                },
                {
                    "name": "Back",
                    "ord": 1,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "media": []
                }
            ],
            "css": ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n\n.cloze {\n font-weight: bold;\n color: blue;\n}",
            "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
            "latexPost": "\\end{document}",
            "req": [[0, "any", [0]]]  # Requirements
        }

        return model

    def _create_default_deck(self):
        """Create a default deck."""
        current_time = int(time.time())

        decks = {
            "1": {
                "id": 1,
                "name": "Default",
                "desc": "",
                "extendRev": 50,
                "usn": 0,
                "collapsed": False,
                "newToday": [0, 0],
                "revToday": [0, 0],
                "lrnToday": [0, 0],
                "timeToday": [0, 0],
                "dyn": 0,
                "extendNew": 10,
                "conf": 1,
                "mod": current_time
            }
        }

        return decks

    def add_model(self, name, fields, templates):
        """Add a new model to the collection."""
        self.connect()
        cursor = self.conn.cursor()

        # Get the current models
        cursor.execute("SELECT models FROM col WHERE id = 1")
        models_json = cursor.fetchone()[0]
        models = json.loads(models_json)

        # Create a new model
        model_id = int(time.time() * 1000)  # Use timestamp as ID
        model = {
            "id": model_id,
            "name": name,
            "type": 0,
            "mod": int(time.time()),
            "usn": 0,
            "sortf": 0,  # Sort by first field
            "tags": [],
            "did": 1,  # Default deck ID
            "tmpls": [],
            "flds": [],
            "css": ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n\n.cloze {\n font-weight: bold;\n color: blue;\n}",
            "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
            "latexPost": "\\end{document}",
            "req": []
        }

        # Add fields
        for i, field_name in enumerate(fields):
            model["flds"].append({
                "name": field_name,
                "ord": i,
                "sticky": False,
                "rtl": False,
                "font": "Arial",
                "size": 20,
                "media": []
            })

        # Add templates
        for i, template in enumerate(templates):
            model["tmpls"].append({
                "name": template["name"],
                "ord": i,
                "qfmt": template["qfmt"],
                "afmt": template["afmt"],
                "bqfmt": "",
                "bafmt": "",
                "did": None,
                "bfont": "",
                "bsize": 0
            })

            # Add requirements
            fields_required = []
            for j, field in enumerate(fields):
                if "{{" + field + "}}" in template["qfmt"] or "{{" + field + "}}" in template["afmt"]:
                    fields_required.append(j)

            model["req"].append([i, "any", fields_required])

        # Add the model to the collection
        models[str(model_id)] = model
        cursor.execute("UPDATE col SET models = ?, mod = ? WHERE id = 1", (json.dumps(models), int(time.time())))
        self.conn.commit()

        return model_id

    def add_deck(self, name):
        """Add a new deck to the collection."""
        self.connect()
        cursor = self.conn.cursor()

        # Get the current decks
        cursor.execute("SELECT decks FROM col WHERE id = 1")
        decks_json = cursor.fetchone()[0]
        decks = json.loads(decks_json)

        # Create a new deck
        deck_id = int(time.time() * 1000)  # Use timestamp as ID
        deck = {
            "id": deck_id,
            "name": name,
            "desc": "",
            "extendRev": 50,
            "usn": 0,
            "collapsed": False,
            "newToday": [0, 0],
            "revToday": [0, 0],
            "lrnToday": [0, 0],
            "timeToday": [0, 0],
            "dyn": 0,
            "extendNew": 10,
            "conf": 1,
            "mod": int(time.time())
        }

        # Add the deck to the collection
        decks[str(deck_id)] = deck
        cursor.execute("UPDATE col SET decks = ?, mod = ? WHERE id = 1", (json.dumps(decks), int(time.time())))
        self.conn.commit()

        return deck_id

    def add_note(self, model_id, deck_id, fields_data, tags=None):
        """Add a new note to the collection."""
        self.connect()
        cursor = self.conn.cursor()

        # Get the model
        cursor.execute("SELECT models FROM col WHERE id = 1")
        models_json = cursor.fetchone()[0]
        models = json.loads(models_json)
        model = models[str(model_id)]

        # Create a new note
        note_id = int(time.time() * 1000)  # Use timestamp as ID
        guid = str(random.randrange(1 << 30, 1 << 31))
        current_time = int(time.time())

        # Join fields with the field separator character (0x1f)
        fields_str = "\x1f".join(fields_data)

        # Sort field is the first field by default
        sfld = fields_data[0]

        # Calculate checksum
        csum = self._checksum(sfld)

        # Join tags with space
        tags_str = " ".join(tags) if tags else ""

        cursor.execute("SELECT COUNT(*) FROM notes WHERE id = ?", (note_id,))
        if cursor.fetchone()[0] == 0:
            pprint.pprint(note_id)
            # Insert the note
            cursor.execute('''
            INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                note_id,
                guid,
                model_id,
                current_time,
                -1,  # usn -1 means the note is new
                tags_str,
                fields_str,
                sfld,
                csum,
                0,  # flags
                ""  # data
            ))

        # Create cards for each template
        for template in model["tmpls"]:
            card_id = int(time.time() * 1000) + template["ord"]  # Use timestamp + template order as ID

            res = cursor.execute("SELECT COUNT(*) FROM col WHERE id = ?", (card_id,))
            pprint.pprint(card_id)
            if res.fetchone()[0] == 0:
                print(f"Inserting: {card_id}")
                cursor.execute('''
                INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    card_id,
                    note_id,
                    deck_id,
                    template["ord"],
                    current_time,
                    -1,  # usn -1 means the card is new
                    0,  # type 0 = new card
                    0,  # queue 0 = new card
                    0,  # due 0 = new card
                    0,  # interval
                    2500,  # factor (default)
                    0,  # reps
                    0,  # lapses
                    0,  # left
                    0,  # odue
                    0,  # odid
                    0,  # flags
                    ""  # data
                ))

        self.conn.commit()
        return note_id

    def _checksum(self, text):
        """Calculate a checksum for a field."""
        # Anki uses a 32-bit unsigned integer checksum
        # This is a simple implementation
        val = 0
        for c in text:
            val = ((val * 31) + ord(c)) & 0xFFFFFFFF
        return val

    def add_media(self, filename, data):
        """Add a media file to be included in the APKG."""
        self.media_files.append((filename, data))

    def export_apkg(self, output_filename):
        """Export the collection as an APKG file."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Copy the database file to the temporary directory
            collection_path = os.path.join(temp_dir, "collection.anki2")
            shutil.copy2(self.db_path, collection_path)

            # Create the media file
            media_path = os.path.join(temp_dir, "media")
            with open(media_path, 'w') as f:
                media_dict = {}
                for i, (filename, _) in enumerate(self.media_files):
                    media_dict[str(i)] = filename
                json.dump(media_dict, f)

            # Write the media files
            for i, (_, data) in enumerate(self.media_files):
                with open(os.path.join(temp_dir, str(i)), 'wb') as f:
                    f.write(data)

            # Create the APKG file
            with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(collection_path, "collection.anki2")
                zipf.write(media_path, "media")

                # Add media files
                for i, _ in enumerate(self.media_files):
                    zipf.write(os.path.join(temp_dir, str(i)), str(i))

            return True

        except Exception as e:
            print(f"Error exporting APKG: {e}")
            return False

        finally:
            # Clean up the temporary directory
            shutil.rmtree(temp_dir)


# Example usage
def main():
    # Create a new flashcard app
    app = AnkiFlashcardApp("mycollection.anki2")

    # Initialize the database
    app.initialize_database()

    # Create a custom model
    fields = ["Question", "Answer", "Example"]
    templates = [
        {
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Answer}}<br><br>Example: {{Example}}"
        }
    ]
    custom_model_id = app.add_model("Custom Model", fields, templates)

    # Create a custom deck
    deck_id = app.add_deck("My Custom Deck")

    # Add notes to the deck
    app.add_note(
        custom_model_id,
        deck_id,
        ["What is Python?", "Python is a high-level programming language.", "print('Hello, World!')"],
        ["programming", "python"]
    )
    app.add_note(
        custom_model_id,
        deck_id,
        ["What is a variable?", "A named location in memory that stores a value.", "x = 10"],
        ["programming", "basics"]
    )

    # Export the collection as an APKG file
    app.export_apkg("mycollection.apkg")

    # Close the database connection
    app.close()


if __name__ == "__main__":
    main()