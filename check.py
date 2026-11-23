import os
import sys
import urllib.request

URL = os.environ["MOVIE_URL"]
TOPIC = os.environ["NTFY_TOPIC"]
MANUAL = os.environ.get("EVENT_NAME") == "workflow_dispatch"

# Text that appears on the page once bookings are open (lowercase).
# If you get false alerts or no alert, tell Claude what the page shows and edit this.
KEYWORDS = ["book tickets"]


def notify(message):
    req = urllib.request.Request(
        f"https://ntfy.sh/{TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": "BookMyShow alert",
            "Click": URL,
            "Priority": "high",
        },
    )
    urllib.request.urlopen(req, timeout=30)


def fetch():
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "en-IN,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


found = False
try:
    html = fetch().lower()
    found = any(k in html for k in KEYWORDS)
    print(f"Page loaded ({len(html)} characters). Bookings open: {found}")
except Exception as e:
    print(f"Could not load the page: {e}")
    if MANUAL:
        notify(f"Test run: could not load the page ({e})")

if found:
    notify("Bookings look open! Tap to open the page.")
elif MANUAL:
    notify("Test run OK: page loaded, bookings not open yet.")

output_file = os.environ.get("GITHUB_OUTPUT")
if output_file:
    with open(output_file, "a") as f:
        f.write(f"found={str(found).lower()}\n")

sys.exit(0)
