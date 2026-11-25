"""
Campus Event Schedule Clash Detector - website version (Flask)

The web page only shows the form and the results. All the real work is done by
the Python functions in clash_detector.py: validation helpers, find_clashes(),
suggest_free_slot(), hours_per_venue(), clash_report() and the CSV functions.

Run:
    python -m pip install flask
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import os
from flask import Flask, jsonify, render_template, request, send_file

import clash_detector as cd

# work inside this folder so events.csv is always found
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# create events.csv if it is missing (same as the menu program)
try:
    with open(cd.EVENTS_FILE, "r", encoding="utf-8"):
        pass
except FileNotFoundError:
    cd.save_events([])


# ------------------------------------------------------------ small helpers
def event_to_json(e):
    return {"id": e["id"], "name": e["name"], "club": e["club"],
            "venue": e["venue"], "date": e["date"], "start": e["start"],
            "end": e["end"], "start_min": e["start_min"], "end_min": e["end_min"]}


def clashes_to_json(clashes):
    result = []
    for kind, other in clashes:
        item = event_to_json(other)
        item["type"] = kind
        result.append(item)
    return result


def slot_to_json(slot):
    if slot is None:
        return None
    return {"start": cd.to_time_text(slot[0]), "end": cd.to_time_text(slot[1]),
            "start_min": slot[0], "end_min": slot[1]}


def build_event(data, need_names):
    """Check the form data with the same rules as the menu program.
    Return (event, error_message)."""
    name = str(data.get("name", "")).strip().replace(",", " ")
    club = str(data.get("club", "")).strip().replace(",", " ")
    venue_text = str(data.get("venue", "")).strip()
    date_text = str(data.get("date", "")).strip()
    start_min = cd.to_minutes(str(data.get("start", "")))
    end_min = cd.to_minutes(str(data.get("end", "")))

    if need_names and (name == "" or club == ""):
        return None, "Event name and club cannot be empty."
    venue = None
    for v in cd.VENUES:
        if v.lower() == venue_text.lower():
            venue = v
    if venue is None:
        return None, "Unknown venue. Valid venues: " + ", ".join(sorted(cd.VENUES))
    if not cd.valid_date(date_text):
        return None, "Invalid date. Use DD-MM-YYYY, for example 15-11-2026."
    if start_min is None or end_min is None:
        return None, "Invalid time. Use 24-hour HH:MM, for example 14:30."
    if end_min <= start_min:
        return None, "End time must be after the start time."
    day, month, year = date_text.split("-")
    date = f"{int(day):02d}-{int(month):02d}-{year}"
    return cd.make_event(0, name, club, venue, date, start_min, end_min), None


# ------------------------------------------------------------------- routes
@app.route("/")
def home():
    return render_template("index.html", venues=sorted(cd.VENUES))


@app.route("/api/events")
def list_events():
    events = cd.sort_events(cd.load_events())
    return jsonify([event_to_json(e) for e in events])


@app.route("/api/check", methods=["POST"])
def check():
    """Live check while the user types: clashes and the nearest free slot."""
    event, error = build_event(request.get_json(force=True), need_names=False)
    if error:
        return jsonify(ready=False, error=error)
    events = cd.load_events()
    clashes = cd.find_clashes(event, events)
    slot = cd.suggest_free_slot(event, events) if clashes else None
    return jsonify(ready=True, event=event_to_json(event),
                   clashes=clashes_to_json(clashes), slot=slot_to_json(slot))


@app.route("/api/add", methods=["POST"])
def add():
    data = request.get_json(force=True)
    event, error = build_event(data, need_names=True)
    if error:
        return jsonify(ok=False, error=error), 400
    events = cd.load_events()
    clashes = cd.find_clashes(event, events)
    if len(clashes) > 0:
        slot = cd.suggest_free_slot(event, events)
        if not data.get("book_suggested") or slot is None:
            return jsonify(ok=False, clashes=clashes_to_json(clashes),
                           slot=slot_to_json(slot))
        event = cd.make_event(0, event["name"], event["club"], event["venue"],
                              event["date"], slot[0], slot[1])
    event["id"] = cd.next_id(events)
    events.append(event)
    cd.save_events(events)
    return jsonify(ok=True, event=event_to_json(event))


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete(event_id):
    events = cd.load_events()
    kept = [e for e in events if e["id"] != event_id]
    if len(kept) == len(events):
        return jsonify(ok=False, error="No event with that ID."), 404
    cd.save_events(kept)
    return jsonify(ok=True)


@app.route("/api/usage")
def usage():
    events = cd.load_events()
    if len(events) == 0:
        return jsonify(venues=[], busiest_day=None)
    totals = cd.hours_per_venue(events)
    ranking = sorted(totals, key=totals.get, reverse=True)
    days = cd.hours_per_day(events)
    busiest = max(days, key=days.get)
    return jsonify(venues=[{"venue": v, "hours": totals[v]} for v in ranking],
                   busiest_day={"date": busiest, "hours": days[busiest]})


@app.route("/api/report")
def report():
    cd.clash_report(cd.load_events())            # writes clash_report.txt
    try:
        with open(cd.REPORT_FILE, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        text = "Could not read the report file."
    return jsonify(text=text)


@app.route("/report.txt")
def download_report():
    return send_file(os.path.abspath(cd.REPORT_FILE), as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

