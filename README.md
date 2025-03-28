# Basketball Flashcards Spaced Repetition Application

## Prerequisites

Before running the application, ensure you have the following installed:
- Python 3.8+
- pip (Python package manager)

## Prompt used on Claude (Claude 3.5 Haiku)
We have discussed last week about a spaced repetition example Python code that takes 10 random basketball flashcards, 
allows the user to review the flashcards, and keep all data into an ANKI-compatible SQLite3 database schema. The schema 
includes an empty 'graves' table. Furthermore, the schema does not have a 'models' table, because all models are placed
in JSON format structure inside column 'models' of table 'col'. Now I need 3 pieces of Python code. In the first, I have
a client that takes options from a numbered user menu that allows the user to review cards, add a new card, show all cards, 
show upcoming reviews and export database to an ANKI APKG file. In the second, I need to have an REST API backend 
flashcard server, where all the database processing necessary to fulfill the user menu in the client is kept. 
The server is implemented using Flask. In the last piece of Python code, a total of 5 test cases for the REST API 
are built for each user menu option in the client side. Finally, detailed instructions are provided to run the 
server as a back-end to the application, as well as to trigger the unit tests of the API interface.

## Claude's Response
I’ve created four artifacts for your spaced repetition basketball flashcards application:
1.	basketball-flashcards-client.py: A client-side application with a menu-driven interface that 
communicates with the REST API backend.
2. basketball-flashcards-server.py: A Flask-based REST API server that handles database operations, 
spaced repetition logic, and Anki export functionality. 
3. basketball-flashcards-tests.py: A comprehensive unit test suite for testing the API endpoints. 
4. basketball-flashcards-readme.md: A detailed README with setup instructions, installation steps, 
and usage guidelines.

Key features of the application:
- Implements SuperMemo-2 spaced repetition algorithm
- Supports adding, reviewing, and managing flashcards
- Exports to Anki-compatible APKG format
- Uses SQLite with an Anki-like schema
- Includes comprehensive unit tests
- Provides a user-friendly CLI interface

The application follows the specifications you mentioned:
- Uses an SQLite database
- Has an empty ‘graves’ table
- Stores models in JSON format in the ‘col’ table
- Supports 10 random cards for review
- Provides a complete REST API backend
Would you like me to elaborate on any part of the implementation or explain any specific aspect of the code?

## Installation

1. Create a new virtual environment (optional but recommended):
```bash
python3 -m venv basketball_flashcards_env
source basketball_flashcards_env/bin/activate  # On Windows, use `basketball_flashcards_env\Scripts\activate`
```

2. Install required dependencies:
```bash
pip install flask requests anki
```

## Running the Application

### Starting the Backend Server

1. Run the Flask backend server:
```bash
python basketball_flashcards_server.py
```
- The server will start on `http://localhost:8000`
- A SQLite database `basketball_flashcards.db` will be created automatically

### Running the Client

In a separate terminal (with the virtual environment activated):
```bash
python basketball_flashcards_client.py
```

## Running Unit Tests

To run the unit tests:
```bash
python basketball_flashcards_tests.py
```

## Application Workflow

1. Start the server first
2. Run the client application
3. Use the numbered menu to:
   - Review Cards
   - Add New Cards
   - Show All Cards
   - Show Upcoming Reviews
   - Export Database to APKG

## Troubleshooting

- Ensure the server is running before starting the client
- Check that all dependencies are installed
- Verify Python version compatibility

## Notes

- The application uses an SQLite database with an Anki-compatible schema
- Spaced repetition is implemented using the SuperMemo-2 algorithm
- Cards are exported in Anki Package (.apkg) format for compatibility with Anki desktop/mobile apps