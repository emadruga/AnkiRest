# Basketball Flashcards REST API Documentation

This document provides detailed information about the REST API endpoints available in the Basketball Flashcards application.

## Base URL

All endpoints are relative to: `http://localhost:8000`

## Endpoints

### 1. Review Cards

#### GET /review

Retrieves cards that are due for review based on the spaced repetition algorithm.

**Request Parameters**
- None

**Response**

*Success (200 OK)*
```json
[
  {
    "id": 1,
    "front": "Who won the most NBA championships?",
    "back": "Bill Russell with 11 championships",
    "due_date": "2025-03-28 10:15:30",
    "ease_factor": 2.5,
    "interval": 1,
    "repetitions": 0
  },
  {
    "id": 2,
    "front": "What NBA team has won the most championships?",
    "back": "Boston Celtics with 17 championships",
    "due_date": "2025-03-28 14:20:45",
    "ease_factor": 2.3,
    "interval": 3,
    "repetitions": 2
  }
  // Up to 10 cards may be returned
]
```

*Success (200 OK) - No cards due*
```json
[]
```

**Error Codes**
- `500 Internal Server Error`: Database error or server issue

---

#### POST /review

Processes a card review, updating its spaced repetition parameters based on user difficulty rating.

**Request Body**
```json
{
  "card_id": 1,
  "difficulty": 4
}
```

**Parameters**
- `card_id` (integer, required): The ID of the reviewed card
- `difficulty` (integer, required): User's recall rating (1-5, where 1 is hardest, 5 is easiest)

**Response**

*Success (200 OK)*
```json
{
  "status": "success"
}
```

*Error (404 Not Found)*
```json
{
  "status": "card not found"
}
```

**Error Codes**
- `400 Bad Request`: Missing or invalid parameters
- `404 Not Found`: Card ID does not exist
- `500 Internal Server Error`: Database error or server issue

---

### 2. Manage Cards

#### GET /cards

Retrieves all flashcards in the database.

**Request Parameters**
- None

**Response**

*Success (200 OK)*
```json
[
  {
    "id": 1,
    "front": "Who won the most NBA championships?",
    "back": "Bill Russell with 11 championships",
    "due_date": "2025-03-28 10:15:30",
    "ease_factor": 2.5,
    "interval": 1,
    "repetitions": 0
  },
  {
    "id": 2,
    "front": "What NBA team has won the most championships?",
    "back": "Boston Celtics with 17 championships",
    "due_date": "2025-03-29 14:20:45",
    "ease_factor": 2.3,
    "interval": 3,
    "repetitions": 2
  }
  // All cards in the database
]
```

*Success (200 OK) - Empty database*
```json
[]
```

**Error Codes**
- `500 Internal Server Error`: Database error or server issue

---

#### POST /cards

Creates a new flashcard.

**Request Body**
```json
{
  "front": "Who is the all-time NBA scoring leader?",
  "back": "LeBron James (38,652 points and counting)"
}
```

**Parameters**
- `front` (string, required): The front content of the flashcard (question)
- `back` (string, required): The back content of the flashcard (answer)

**Response**

*Success (201 Created)*
```json
{
  "id": 3
}
```

**Error Codes**
- `400 Bad Request`: Missing or invalid parameters
- `500 Internal Server Error`: Database error or server issue

---

### 3. Upcoming Reviews

#### GET /upcoming

Retrieves cards scheduled for future review.

**Request Parameters**
- None

**Response**

*Success (200 OK)*
```json
[
  {
    "id": 3,
    "front": "Who is the all-time NBA scoring leader?",
    "back": "LeBron James (38,652 points and counting)",
    "due_date": "2025-03-30 09:45:20",
    "ease_factor": 2.5,
    "interval": 2,
    "repetitions": 1
  },
  {
    "id": 4,
    "front": "What is the record for most points scored in an NBA game?",
    "back": "100 points by Wilt Chamberlain (March 2, 1962)",
    "due_date": "2025-04-02 16:30:15",
    "ease_factor": 2.7,
    "interval": 5,
    "repetitions": 3
  }
  // All upcoming cards ordered by due date
]
```

*Success (200 OK) - No upcoming reviews*
```json
[]
```

**Error Codes**
- `500 Internal Server Error`: Database error or server issue

---

### 4. Export Database

#### GET /export

Exports the database to an Anki Package (.apkg) file.

**Request Parameters**
- None

**Response**

*Success (200 OK)*
```json
{
  "status": "exported",
  "filename": "basketball_flashcards.apkg"
}
```

**Error Codes**
- `500 Internal Server Error`: Database error, file system error, or server issue

---

## Error Handling

All endpoints may return the following general error responses:

**400 Bad Request**
- Returned when the request is malformed or missing required parameters

**404 Not Found**
- Returned when a requested resource (e.g., a specific card) does not exist

**500 Internal Server Error**
- Returned when an unexpected server error occurs

## Data Models

### Card Object

```json
{
  "id": 1,
  "front": "Question text goes here",
  "back": "Answer text goes here",
  "due_date": "2025-03-28 10:15:30",
  "ease_factor": 2.5,
  "interval": 1,
  "repetitions": 0
}
```

**Fields**
- `id` (integer): Unique identifier for the card
- `front` (string): Front content of the flashcard (question)
- `back` (string): Back content of the flashcard (answer)
- `due_date` (string): Date and time when the card is due for review (ISO format)
- `ease_factor` (float): SuperMemo-2 ease factor
- `interval` (integer): Current interval in days
- `repetitions` (integer): Number of times the card has been reviewed
