#!/usr/bin/env bash
# Using manage.py as main entrypoint to app by forwarding the typical
# "manage.py" commands off to flask's utlitiy script.
echo "Forwarding command to flask utility script"
echo
echo "  FLASK_APP=psi.cli:application flask $@"
echo
exec env FLASK_APP=psi.cli:application flask $@
