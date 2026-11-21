# Campus Event Schedule Clash Detector

A menu-driven Python application that helps college clubs and campus administrators manage event schedules, detect booking conflicts, and find alternative time slots.

## Overview

Campus clubs organise workshops, talks, rehearsals, competitions, and other events. When venue bookings are handled informally, two events can end up using the same venue at the same time. A club can also be scheduled to run two events simultaneously at different locations.

The **Campus Event Schedule Clash Detector** addresses these problems by storing event details, checking for venue and organiser conflicts, suggesting an alternative free slot, summarising venue usage, and generating a clash report.

## Features

- **Add events:** Enter the event name, club, venue, date, start time, and end time.
- **Input validation:** Rejects empty fields, invalid dates or times, unknown venues, and end times that are not later than start times.
- **Venue clash detection:** Detects overlapping events booked at the same venue on the same date.
- **Organiser clash detection:** Detects overlapping events organised by the same club, even if they use different venues.
- **Free-slot suggestion:** When a clash is detected, searches for a nearby available slot at the requested venue.
- **View all events:** Displays saved events in date and time order.
- **Day timetable:** Displays the events scheduled for a selected date.
- **Search events:** Finds events using a club name or venue.
- **Venue usage summary:** Calculates booked hours per venue and identifies the busiest venue and day.
- **Clash report:** Generates a text file containing detected clashes and the details of the events involved.
- **Edit and delete:** Updates or removes an event using its event ID.

## Requirements

- Python 3.x
- No third-party Python packages are required. The project uses Python's built-in `datetime` module.

## Getting Started

1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Run the program:

   ```bash
   python clash_detector.py
   ```

   If your system uses `python3`, run:

   ```bash
   python3 clash_detector.py
   ```

> If the Python file has a different name in your repository, replace `clash_detector.py` with that filename.

## How to Use

When the program starts, it displays this menu:

```text
===== Campus Event Schedule Clash Detector =====
1. Add event          5. Venue usage summary
2. View all events    6. Generate clash report
3. Day timetable      7. Edit / delete event
4. Search events      8. Exit
```

Choose an option from 1 to 8 and follow the prompts.

### Adding an event

Provide the requested details:

- Event name
- Club name
- Venue
- Date in `DD-MM-YYYY` format
- Start time in 24-hour `HH:MM` format
- End time in 24-hour `HH:MM` format

If the event conflicts with an existing booking, the program displays the clash and may suggest an alternative slot. You can choose whether to book the suggested slot.

## Scheduling Rules

- Dates must be valid calendar dates in `DD-MM-YYYY` format.
- Times must use the 24-hour `HH:MM` format.
- The end time must be later than the start time.
- Events are compared only when they occur on the same date.
- Two events overlap when:

  ```python
  start1 < end2 and start2 < end1
  ```

- Back-to-back events are allowed. For example, an event ending at `15:00` does not clash with one starting at `15:00`.
- A venue clash occurs when overlapping events use the same venue.
- An organiser clash occurs when overlapping events belong to the same club.
- Free-slot suggestions are searched within the working hours of **09:00 to 18:00** and must be long enough for the requested event.

## Data and Generated Files

The program creates and uses these files in its working directory:

| File | Purpose |
|---|---|
| `events.csv` | Stores event IDs, names, clubs, venues, dates, and start/end times. Created automatically if missing. |
| `clash_report.txt` | Generated clash report, including the date and details of each conflicting event. |

Keep `events.csv` in the same working directory as the Python program so previously saved events can be loaded.

## Python Concepts Used

The project demonstrates core concepts from the Computational Thinking and Programming course:

- Variables and data types
- Conditional statements (`if`, `elif`, `else`)
- `while` and `for` loops
- Lists, tuples, dictionaries, and sets
- Functions with parameters and return values
- String handling
- The built-in `datetime` module
- File handling
- Exception handling with `try` and `except`
- Bubble sort for ordering events and time intervals

The program converts times into minutes after midnight to make time comparisons and duration calculations easier. For example, `09:30` becomes `570`.

## Team

Project developed as part of **Computational Thinking and Programming (2026CSAE100)** at Bennett University, Academic Year 2026–27.

- Shreya Choudhary
- Anshul
- Ayush Singh
- Avishi Khandelwal
- Pratiksha Mishra

## Future Improvements

Possible extensions include:

- Adding a 15-minute buffer between events at the same venue.
- Checking venue capacity against expected attendance.
- Generating a weekly timetable.
- Displaying venue usage in a chart.
- ## Acknowledgements

- Python documentation: https://docs.python.org/3/
- Allen B. Downey, *Think Python*.
- Course material for Computational Thinking and Programming (2026CSAE100).

---



