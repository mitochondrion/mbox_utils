#!/usr/bin/env python3
import sys
import re
from email.utils import parsedate, parseaddr, getaddresses
import time

def usage():
    print('Usage: extract_emails.py <input.mbox> <output.txt> <search term>')
    print('  Search term matches against name or email address in From/To headers (case-insensitive partial match)')
    sys.exit(1)

def parse_date_str(envelope_line):
    m = re.match(r'^From \S+ (.+)$', envelope_line)
    if m:
        t = parsedate(m.group(1))
        if t:
            return time.strftime('%-m/%-d/%y %-I:%M %p', t)
    return '(unknown date)'

def format_addr(name, email):
    if name and email:
        return f'{email} <{name}>'
    return name or email or '(unknown)'

def addrs_from_header(header_val):
    return getaddresses([header_val]) if header_val else []

def search_matches(headers, term):
    for key in ('from', 'to', 'cc'):
        val = headers.get(key, '')
        if term in val.lower():
            return True
    return False

def format_addrlist(header_val):
    if not header_val:
        return '(none)'
    addrs = getaddresses([header_val])
    return ', '.join(format_addr(n, e) for n, e in addrs)

def strip_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def process_message(buffer, term, fout):
    envelope = buffer[0]
    headers = {}
    in_headers = True
    body_lines = []

    for line in buffer[1:]:
        if in_headers:
            if line.strip() == '':
                in_headers = False
            else:
                m = re.match(r'^([\w-]+):\s*(.+)', line)
                if m:
                    key = m.group(1).lower()
                    # handle folded headers
                    headers[key] = m.group(2).strip()
        else:
            body_lines.append(line.rstrip())

    if 'chat' in headers.get('x-gmail-labels', '').lower():
        return False

    if not search_matches(headers, term):
        return False

    date_str = parse_date_str(envelope)
    from_str = format_addrlist(headers.get('from', ''))
    to_str = format_addrlist(headers.get('to', ''))
    subject = headers.get('subject', '(no subject)')
    body = strip_html('\n'.join(body_lines))

    fout.write('===\n')
    fout.write(f'From: {from_str}\n')
    fout.write(f'To: {to_str}\n')
    fout.write(f'Date: {date_str}\n')
    fout.write(f'Subject: {subject}\n')
    fout.write('Body:\n')
    fout.write(body + '\n')
    fout.write('\n')
    return True

if len(sys.argv) != 4:
    usage()

mbox_path = sys.argv[1]
out_path = sys.argv[2]
term = sys.argv[3].lower()

count = 0
exported = 0

with open(mbox_path, 'r', errors='replace') as fin, \
     open(out_path, 'w') as fout:

    buffer = []
    for line in fin:
        if line.startswith('From ') and buffer:
            if process_message(buffer, term, fout):
                exported += 1
                if exported % 10 == 0:
                    print(f'\r{count} scanned, {exported} exported', end='', flush=True, file=sys.stderr)
            count += 1
            if count % 1000 == 0:
                print(f'\r{count} scanned, {exported} exported', end='', flush=True, file=sys.stderr)
            buffer = [line]
        else:
            buffer.append(line)

    if buffer:
        if process_message(buffer, term, fout):
            exported += 1

print(f'\nDone. {count} messages scanned, {exported} exported to {out_path}', file=sys.stderr)
