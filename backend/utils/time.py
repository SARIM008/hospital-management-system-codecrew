from datetime import datetime, timedelta


def generate_slots(start_time, end_time, duration):
    slots = []
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)

    while current + timedelta(minutes=duration) <= end:
        slots.append(current.time())
        current += timedelta(minutes=duration)

    return slots


def parse_date(date_string):
    if not date_string:
        return None
    try:
        # Converts the HTML5 string "YYYY-MM-DD" into a Python Date object
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        return None