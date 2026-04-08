#!/usr/bin/env python3
import sys
import re
from collections import defaultdict
from email.utils import parsedate, parseaddr
import time

def parse_date_ts(envelope_line):
    m = re.match(r'^From \S+ (.+)$', envelope_line)
    if m:
        t = parsedate(m.group(1))
        if t:
            ts = time.mktime(t)
            return ts, time.strftime('%-m/%-d/%y %-I:%M %p', t), time.strftime('%-m/%-d/%y', t)
    return None, '(unknown date)', '(unknown)'

def parse_mbox(path):
    threads = defaultdict(lambda: {'first_ts': None, 'first_date': '', 'participants': set(), 'participants_full': set(), 'messages': []})
    count = 0

    with open(path, 'r', errors='replace') as f:
        buffer = []
        for line in f:
            if line.startswith('From ') and buffer:
                process_message(buffer, threads)
                count += 1
                if count % 1000 == 0:
                    print('.', end='', flush=True, file=sys.stderr)
                buffer = [line]
            else:
                buffer.append(line)
        if buffer:
            process_message(buffer, threads)
            count += 1

    print(f' {count} messages.', file=sys.stderr)
    return threads

def process_message(buffer, threads):
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
                    headers[m.group(1).lower()] = m.group(2).strip()
        else:
            body_lines.append(line.rstrip())

    thread_id = headers.get('x-gm-thrid', '(none)')
    sender_raw = headers.get('from', '')
    sender_name, sender_email = parseaddr(sender_raw)
    display_name = sender_name or sender_email
    full = f'{sender_name} <{sender_email}>' if sender_name and sender_email else display_name

    ts, date_str, short_date = parse_date_ts(envelope)
    body = ' '.join(body_lines).strip()
    body = re.sub(r'<[^>]+>', '', body).strip()

    t = threads[thread_id]
    if ts and (t['first_ts'] is None or ts < t['first_ts']):
        t['first_ts'] = ts
        t['first_date'] = short_date
    t['participants'].add(display_name)
    t['participants_full'].add(full)
    t['messages'].append({
        'date': date_str,
        'sender': display_name,
        'body': body,
    })

def write_output(threads, out_path):
    sorted_threads = sorted(threads.items(), key=lambda x: x[1]['first_ts'] or 0)

    with open(out_path, 'w') as f:
        # index
        for tid, t in sorted_threads:
            participants = ', '.join(sorted(t['participants_full']))
            f.write(f"[{tid}][{t['first_date']}][{participants}]\n")

        f.write('\n')

        # threads
        for tid, t in sorted_threads:
            participants = ', '.join(sorted(t['participants']))
            f.write(f'=== {tid}\n')
            f.write(f'Participants: {participants}\n')
            f.write('---\n')
            for msg in t['messages']:
                f.write(f"{msg['date']} - {msg['sender']}: {msg['body']}\n")
            f.write('\n')

if len(sys.argv) != 3:
    print('Usage: chat_threads.py <chats.mbox> <output.txt>')
    sys.exit(1)

mbox_path = sys.argv[1]
out_path = sys.argv[2]

print('Parsing mbox', end='', file=sys.stderr)
threads = parse_mbox(mbox_path)
print(f'{len(threads)} threads found.', file=sys.stderr)
print('Writing output...', file=sys.stderr)
write_output(threads, out_path)
print(f'Done. Written to {out_path}', file=sys.stderr)
