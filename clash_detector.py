"""
Campus Event Schedule Clash Detector
Course: Computational Thinking and Programming (2026CSAE100)
 
A menu-driven program where clubs add events. It detects venue clashes and
organizer (club) clashes, suggests the nearest free slot, shows venue usage
and writes a clash report.
 
Key idea: every time is converted to minutes after midnight (9:30 -> 570),
so comparing and subtracting times is easy without the datetime module.
Dates are typed as DD-MM-YYYY and times as HH:MM (24-hour).
"""
 
import csv
import os
from datetime import datetime
 
# ---------------------------------------------------------------- settings
EVENTS_FILE = "events.csv"
REPORT_FILE = "clash_report.txt"
FIELDS = ["id", "name", "club", "venue", "date", "start", "end"]
 
# Set of valid venues (add your campus venues here)
VENUES = {"Auditorium", "Seminar Hall", "Room 101", "Room 102", "Sports Ground"}
 
WORK_START = 9 * 60    # 09:00 in minutes
WORK_END = 18 * 60     # 18:00 in minutes
 
 
# ------------------------------------------------------------ time helpers
def to_minutes(text):
    """Convert 'HH:MM' to minutes after midnight. Return None if invalid."""
    parts = text.strip().split(":")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return None
    hours, minutes = int(parts[0]), int(parts[1])
    if hours > 23 or minutes > 59:
        return None
    return hours * 60 + minutes
 
 
def to_time_text(minutes):
    """Convert minutes after midnight back to 'HH:MM'."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
 
 
def valid_date(text):
    """Return True if text is a real date in DD-MM-YYYY format."""
    try:
        datetime.strptime(text.strip(), "%d-%m-%Y")
        return True
    except ValueError:
        return False
 
 
def date_key(text):
    """Sort key so dates are ordered properly (not as plain text)."""
    return datetime.strptime(text, "%d-%m-%Y")
 
 
# ----------------------------------------------------------- file handling
def load_events():
    """Read all events from the CSV file. Missing or empty file -> empty list."""
    events = []
    if not os.path.exists(EVENTS_FILE):
        return events
    try:
        with open(EVENTS_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    row["id"] = int(row["id"])
                    row["start_min"] = to_minutes(row["start"])
                    row["end_min"] = to_minutes(row["end"])
                    if row["start_min"] is None or row["end_min"] is None:
                        continue          # skip damaged rows
                    events.append(row)
                except (KeyError, ValueError, TypeError):
                    continue              # skip damaged rows
    except OSError:
        print("Could not read the events file.")
    return events
 
 
def save_events(events):
    """Write all events to the CSV file."""
    try:
        with open(EVENTS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(events)
    except OSError:
        print("Could not save the events file.")
 
 
def next_id(events):
    """Next free event id."""
    return max((e["id"] for e in events), default=0) + 1
 
 
def make_event(event_id, name, club, venue, date, start_min, end_min):
    """Build one event dictionary."""
    return {"id": event_id, "name": name, "club": club, "venue": venue,
            "date": date, "start": to_time_text(start_min),
            "end": to_time_text(end_min),
            "start_min": start_min, "end_min": end_min}
 
 
# ---------------------------------------------------------- input helpers
def ask_text(prompt):
    """Ask until the answer is not empty."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty. Try again.")
 
 
def ask_date(prompt="Date (DD-MM-YYYY): "):
    while True:
        value = input(prompt).strip()
        if valid_date(value):
            return datetime.strptime(value, "%d-%m-%Y").strftime("%d-%m-%Y")
        print("  Invalid date. Use DD-MM-YYYY, for example 15-11-2026.")
 
 
def ask_time(prompt):
    """Ask until a valid HH:MM time is given. Return (text, minutes)."""
    while True:
        value = input(prompt).strip()
        minutes = to_minutes(value)
        if minutes is not None:
            return to_time_text(minutes), minutes
        print("  Invalid time. Use 24-hour HH:MM, for example 14:30.")
 
 
def ask_venue():
    while True:
        value = input("Venue: ").strip()
        for venue in VENUES:
            if venue.lower() == value.lower():
                return venue
        print("  Unknown venue. Valid venues: " + ", ".join(sorted(VENUES)))
 
 
def ask_event_details():
    """Ask for all event fields with validation. Return a tuple of values."""
    name = ask_text("Event name: ")
    club = ask_text("Club: ")
    venue = ask_venue()
    date = ask_date()
    _, start_min = ask_time("Start time (HH:MM): ")
    while True:
        _, end_min = ask_time("End time (HH:MM): ")
        if end_min > start_min:
            break
        print("  End time must be after the start time.")
    return name, club, venue, date, start_min, end_min
 
 
# ------------------------------------------------- computational feature 1
def overlaps(start1, end1, start2, end2):
    """True if two time ranges overlap. Back-to-back (end == start) is fine."""
    return start1 < end2 and start2 < end1
 
 
def find_clashes(new_event, events, ignore_id=None):
    """
    Compare new_event with saved events on the same date.
    Return a list of (clash_type, other_event).
    """
    clashes = []
    for other in events:
        if other["id"] == ignore_id or other["date"] != new_event["date"]:
            continue
        if not overlaps(new_event["start_min"], new_event["end_min"],
                        other["start_min"], other["end_min"]):
            continue
        if other["venue"] == new_event["venue"]:
            clashes.append(("Venue clash", other))
        if other["club"].lower() == new_event["club"].lower():
            clashes.append(("Organizer clash", other))
    return clashes
 
 
# ------------------------------------------------- computational feature 2
def suggest_free_slot(new_event, events, ignore_id=None):
    """
    Find the free slot nearest to the requested start time at the same venue
    and date, within working hours. Return (start, end) in minutes or None.
    """
    duration = new_event["end_min"] - new_event["start_min"]
    # (start, end) tuples of the venue's busy times that day, sorted by time
    busy = sorted((e["start_min"], e["end_min"]) for e in events
                  if e["venue"] == new_event["venue"]
                  and e["date"] == new_event["date"]
                  and e["id"] != ignore_id)
 
    # Find gaps between busy times inside working hours
    gaps = []
    cursor = WORK_START
    for start, end in busy:
        if start > cursor:
            gaps.append((cursor, min(start, WORK_END)))
        cursor = max(cursor, end)
    if cursor < WORK_END:
        gaps.append((cursor, WORK_END))
 
    # In every gap that is long enough, try the start nearest to the wish
    # first, then every 15 minutes inside the gap (so a slot is still found
    # when the nearest one is blocked, e.g. the club is busy elsewhere)
    best = None
    for gap_start, gap_end in gaps:
        if gap_end - gap_start < duration:
            continue
        latest_start = gap_end - duration
        ideal = min(max(new_event["start_min"], gap_start), latest_start)
        starts = [ideal] + list(range(gap_start, latest_start + 1, 15))
        for candidate in starts:
            trial = dict(new_event, start_min=candidate, end_min=candidate + duration)
            if find_clashes(trial, events, ignore_id):
                continue
            distance = abs(candidate - new_event["start_min"])
            if best is None or distance < best[0]:
                best = (distance, candidate, candidate + duration)
    return (best[1], best[2]) if best else None
 
 
# ----------------------------------------------------------------- display
def print_events(events, title="Events"):
    if not events:
        print("\nNo events to show.")
        return
    print(f"\n{title}")
    print("-" * 86)
    print(f"{'ID':<4}{'Name':<22}{'Club':<16}{'Venue':<15}{'Date':<12}{'Time':<11}")
    print("-" * 86)
    for e in events:
        print(f"{e['id']:<4}{e['name'][:20]:<22}{e['club'][:14]:<16}"
              f"{e['venue']:<15}{e['date']:<12}{e['start']}-{e['end']}")
    print("-" * 86)
 
 
def sorted_events(events):
    return sorted(events, key=lambda e: (date_key(e["date"]), e["start_min"]))
 
 
def sort_events(events):
    """Same as sorted_events(); the website and window versions call this name."""
    return sorted_events(events)
 
 
def show_clashes(clashes):
    for kind, other in clashes:
        print(f"  ! {kind} with event #{other['id']} '{other['name']}' "
              f"({other['club']}, {other['venue']}, {other['date']} "
              f"{other['start']}-{other['end']})")
 
 
# -------------------------------------------------------------- menu items
def add_event(events):
    print("\n--- Add event ---")
    name, club, venue, date, start_min, end_min = ask_event_details()
    event = make_event(next_id(events), name, club, venue, date, start_min, end_min)
 
    clashes = find_clashes(event, events)
    if clashes:
        print("\nThis event clashes:")
        show_clashes(clashes)
        slot = suggest_free_slot(event, events)
        if slot is None:
            print(f"No free slot of that length at {venue} on {date} "
                  f"between {to_time_text(WORK_START)} and {to_time_text(WORK_END)}.")
            print("Event NOT saved.")
            return
        print(f"Suggested free slot at {venue}: "
              f"{to_time_text(slot[0])}-{to_time_text(slot[1])}")
        if input("Book the suggested slot instead? (y/n): ").strip().lower() != "y":
            print("Event NOT saved.")
            return
        event = make_event(event["id"], name, club, venue, date, slot[0], slot[1])
 
    events.append(event)
    save_events(events)
    print(f"Event #{event['id']} saved ({event['start']}-{event['end']}).")
 
 
def view_day(events):
    date = ask_date()
    day = sorted(e for e in events if e["date"] == date) if False else \
        sorted((e for e in events if e["date"] == date), key=lambda e: e["start_min"])
    print_events(day, f"Timetable for {date}")
 
 
def search_events(events):
    term = ask_text("Search by club or venue: ").lower()
    found = [e for e in sorted_events(events)
             if term in e["club"].lower() or term in e["venue"].lower()]
    print_events(found, f"Results for '{term}'")
 
 
def hours_per_venue(events):
    """Dictionary: venue -> total hours booked."""
    totals = {}
    for e in events:
        hours = (e["end_min"] - e["start_min"]) / 60
        totals[e["venue"]] = totals.get(e["venue"], 0) + hours
    return totals
 
 
def hours_per_day(events):
    """Dictionary: date -> total hours booked (all venues)."""
    totals = {}
    for e in events:
        hours = (e["end_min"] - e["start_min"]) / 60
        totals[e["date"]] = totals.get(e["date"], 0) + hours
    return totals
 
 
def venue_usage(events):
    if not events:
        print("\nNo events yet.")
        return
    totals = hours_per_venue(events)
    ranking = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    print("\n--- Venue usage ranking ---")
    for position, (venue, hours) in enumerate(ranking, start=1):
        print(f"{position}. {venue:<15}{hours:.2f} hours")
    days = hours_per_day(events)
    busiest_day = max(days, key=days.get)
    print(f"\nBusiest venue: {ranking[0][0]} ({ranking[0][1]:.2f} hours)")
    print(f"Busiest day  : {busiest_day} ({days[busiest_day]:.2f} hours)")
 
 
def clash_report(events):
    """Write every clash found in the saved events to a TXT file."""
    lines = ["CAMPUS EVENT CLASH REPORT",
             f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ""]
    count = 0
    ordered = sorted_events(events)
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if a["date"] != b["date"]:
                continue
            if not overlaps(a["start_min"], a["end_min"], b["start_min"], b["end_min"]):
                continue
            kinds = []
            if a["venue"] == b["venue"]:
                kinds.append("Venue clash")
            if a["club"].lower() == b["club"].lower():
                kinds.append("Organizer clash")
            if not kinds:
                continue
            count += 1
            lines.append(f"Clash {count}: {' + '.join(kinds)} on {a['date']}")
            for e in (a, b):
                lines.append(f"  #{e['id']} {e['name']} | {e['club']} | "
                             f"{e['venue']} | {e['start']}-{e['end']}")
            lines.append("")
    if count == 0:
        lines.append("No clashes found.")
    else:
        lines.append(f"Total clashes: {count}")
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"\nReport written to {REPORT_FILE} ({count} clash(es) found).")
    except OSError:
        print("Could not write the report file.")
 
 
def edit_or_delete(events):
    print_events(sorted_events(events), "All events")
    if not events:
        return
    try:
        event_id = int(input("Enter the event ID: ").strip())
    except ValueError:
        print("Invalid ID.")
        return
    target = next((e for e in events if e["id"] == event_id), None)
    if target is None:
        print("No event with that ID.")
        return
 
    choice = input("(e)dit or (d)elete? ").strip().lower()
    if choice == "d":
        if input(f"Delete '{target['name']}'? (y/n): ").strip().lower() == "y":
            events.remove(target)
            save_events(events)
            print("Event deleted.")
    elif choice == "e":
        print("Enter the new details.")
        name, club, venue, date, start_min, end_min = ask_event_details()
        updated = make_event(event_id, name, club, venue, date, start_min, end_min)
        clashes = find_clashes(updated, events, ignore_id=event_id)
        if clashes:
            print("Edit cancelled, the new details clash:")
            show_clashes(clashes)
            slot = suggest_free_slot(updated, events, ignore_id=event_id)
            if slot:
                print(f"Free slot nearby: {to_time_text(slot[0])}-{to_time_text(slot[1])}")
            return
        events[events.index(target)] = updated
        save_events(events)
        print("Event updated.")
    else:
        print("No change made.")
 
 
# -------------------------------------------------------------------- main
MENU = """
===== Campus Event Schedule Clash Detector =====
1. Add event          5. Venue usage summary
2. View all events    6. Generate clash report
3. Day timetable      7. Edit / delete event
4. Search events      8. Exit
"""
 
 
def main():
    events = load_events()
    if not os.path.exists(EVENTS_FILE):
        save_events(events)             # create the file if it is missing
    while True:
        print(MENU)
        choice = input("Enter choice (1-8): ").strip()
        if choice == "1":
            add_event(events)
        elif choice == "2":
            print_events(sorted_events(events), "All events")
        elif choice == "3":
            view_day(events)
        elif choice == "4":
            search_events(events)
        elif choice == "5":
            venue_usage(events)
        elif choice == "6":
            clash_report(events)
        elif choice == "7":
            edit_or_delete(events)
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Please enter a number from 1 to 8.")
 
 
# This check lets other files (like clash_gui.py) import the functions above
# without starting the menu. Running this file directly still starts the menu.
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed.")
 
