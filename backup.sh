#!/usr/bin/env bash

timestamp() {
  date
}

stamp=$(timestamp)
stamp="${stamp// /_}"

sqlite3 db.sqlite3 ".backup '${stamp}_db.sqlite3'"
