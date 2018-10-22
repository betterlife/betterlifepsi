#!/usr/bin/env python
import sys
args = ' '.join(sys.argv[1:])
print(f"""Deprecated as of commit 959939b771. Use flask utility script instead:

$ flask {args}
""")
raise SystemExit(1)
