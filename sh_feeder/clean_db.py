#!/usr/bin/env python3

"""
Run this periodically to remove already posted data
usage: ./clean_db.py <sqlite file>
"""

import os.path, sqlite3, sys


def main():
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "feed.db"
    old_size = os.path.getsize(file)
    print("Vacuuming %s..." % file)
    print("Starting size:\t%s bytes" % old_size)
    conn = sqlite3.connect(file)
    conn.execute(
        "UPDATE feeds SET body = '', summary = '', title = '', link = '', \
        image = '', image_title = '', hashtags = '' WHERE posted = 1"
    )
    conn.commit()
    conn.execute("VACUUM")
    new_size = os.path.getsize(file)
    percent = ((old_size - new_size) / old_size) * 100.0
    print("New size:\t%s bytes" % new_size)
    print("Recovered:\t%.2f%%" % percent)


main()
