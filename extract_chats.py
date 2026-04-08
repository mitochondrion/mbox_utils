#!/usr/bin/env python3
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]

with open(input_path, 'r', errors='replace') as fin, \
     open(output_path, 'w') as fout:

    in_chat = False
    buffer = []
    total = 0
    exported = 0

    for line in fin:
        if line.startswith('From '):
            if in_chat and buffer:
                fout.writelines(buffer)
                exported += 1
                if exported % 100 == 0:
                    print(exported, end='', flush=True)
            buffer = [line]
            in_chat = False
            total += 1
            if total % 100 == 0:
                print('.', end='', flush=True)
        else:
            buffer.append(line)
            if not in_chat and line.startswith('X-Gmail-Labels: Chat'):
                in_chat = True

    # handle last message
    if in_chat and buffer:
        fout.writelines(buffer)
        exported += 1

    print(f'\nDone. {total} messages scanned, {exported} chats exported.')
