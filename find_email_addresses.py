#!/usr/bin/env python3
import sys
import re
from email.utils import getaddresses

if len(sys.argv) != 3:
    print('Usage: list_addresses.py <input.mbox> <search term>')
    sys.exit(1)

mbox_path = sys.argv[1]
term = sys.argv[2].lower()

def search_matches(headers, term):
    for key in ('from', 'to', 'cc'):
        val = headers.get(key, '')
        if term in val.lower():
            return True
    return False

found = set()
count = 0

with open(mbox_path, 'r', errors='replace') as f:
    buffer = []
    for line in f:
        if line.startswith('From ') and buffer:
            headers = {}
            in_headers = True
            for bline in buffer[1:]:
                if in_headers:
                    if bline.strip() == '':
                        in_headers = False
                    else:
                        m = re.match(r'^([\w-]+):\s*(.+)', bline)
                        if m:
                            headers[m.group(1).lower()] = m.group(2).strip()
                else:
                    break

            if 'chat' not in headers.get('x-gmail-labels', '').lower() and search_matches(headers, term):
                for name, email in getaddresses([headers.get('from',''), headers.get('to',''), headers.get('cc','')]):
                    if email and (term in email.lower() or term in name.lower()):
                        found.add((email.lower(), name))

            count += 1
            if count % 10000 == 0:
                print(f'{count} scanned...', file=sys.stderr)
            buffer = [line]
        else:
            buffer.append(line)

for email, name in sorted(found):
    if name:
        print(f'{email} <{name}>')
    else:
        print(email)

print(f'\nDone. {count} messages scanned, {len(found)} unique addresses found.', file=sys.stderr)
