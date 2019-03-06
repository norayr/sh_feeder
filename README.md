## CURRENTLY A WIP - DO NOT USE!

# pod_feeder_v2

Publishes RSS/Atom feeds to Diaspora*

This is a lightweight, customizable "bot" script to harvest RSS/Atom feeds and
re-publish them to the Diaspora social network. It is posted here without
warranty, for public use.

v2 is a complete re-write of the
[original pod_feeder](https://github.com/rev138/pod_feeder) script which was
written (poorly) in perl and is no longer supported. Migrating to this version
is recommended.

## Installation
pod_feeder_v2 requires >= python 3.5. You can easily install the dependencies
with pip:

`$ pip3 install -r requirements.txt`

## Migrating from pod_feeder "classic"
1. pod_feeder_v2's database schema is backward-compatible with the original, so
you can point the script at your existing `feed.db` file (or whatever
yours is called).

2. the `--title-tags` and `--url-tags` arguments have not been carried forward
because in practice they generally create lots of spurious tags, and the
'stop words' feature is difficult to implement.