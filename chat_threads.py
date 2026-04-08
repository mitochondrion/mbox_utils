#!/usr/bin/env python3
import sys
import re
from collections import defaultdict
from email.utils import parsedate, parseaddr
import time

def parse_date(envelope_line):
    m = re.match(r'^From \S+ (.+)$', envelope_line)
    if m:
        t = parsedate(m.group(1))
        if t:
            return time.mktime(t), time.strftime('%-m/%-d/%y %-I:%M %p', t)
    return None, '(unknown date)'

def parse_mbox(path):
    threads = defaultdict(lambda: {'first_ts': None, 'first_date': '', 'participants': set(), 'messages': []})
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
    sender_name = parseaddr(sender_raw)[0] or parseaddr(sender_raw)[1]
    ts, date_str = parse_date(envelope)
    body = ' '.join(body_lines).strip()
    body = re.sub(r'<[^>]+>', '', body).strip()

    t = threads[thread_id]
    if ts and (t['first_ts'] is None or ts < t['first_ts']):
        t['first_ts'] = ts
        t['first_date'] = time.strftime('%-m/%-d/%y', time.localtime(ts))
    t['participants'].add(sender_name)
    t['messages'].append({
        'date': date_str,
        'sender': sender_name,
        'body': body,
    })

def list_threads(threads):
    for tid, t in sorted(threads.items(), key=lambda x: x[1]['first_ts'] or 0):
        participants = ', '.join(sorted(t['participants']))
        print(f"[{tid}][{t['first_date']}][{participants}]")

def dump_thread(threads, thread_id):
    t = threads.get(thread_id)
    if not t:
        print(f'Thread {thread_id} not found.')
        sys.exit(1)
    for msg in t['messages']:
        print(f"{msg['date']} - {msg['sender']}: {msg['body']}")

if len(sys.argv) < 2:
    print('Usage: chat_threads.py <chats.mbox> [thread-id]')
    sys.exit(1)

mbox_path = sys.argv[1]
thread_id = sys.argv[2] if len(sys.argv) > 2 else None

print('Parsing mbox', end='', file=sys.stderr)
threads = parse_mbox(mbox_path)
print(f'{len(threads)} threads found.', file=sys.stderr)

if thread_id:
    dump_thread(threads, thread_id)
else:
    list_threads(threads)
