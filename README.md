# Google Takeout Mail Tools

A collection of Python scripts for working with Google Takeout mbox and Hangouts JSON archives.

---

## extract_chats.py

Extracts only chat messages from a Gmail mbox export into a smaller mbox file, suitable for loading into Thunderbird or neomutt.

```bash
python3 extract_chats.py <input.mbox> <output.mbox>
```

---

## chat_threads.py

Parses a chats mbox into a single readable text file with an index and full conversation threads. Browse with `less` or `vim` or whatever.

```bash
python3 chat_threads.py <chats.mbox> <output.txt>
```

**Example:**
```bash
python3 chat_threads.py chats_only.mbox chats.txt
less chats.txt
# use /=== THREAD_ID to jump to a specific thread
```

**Output format:**
```
[THREAD_ID][5/19/12][Ignatius J. Reilly <ignatius@lsu.edu>, Walker Percy]
...

=== THREAD_ID
Participants: Ignatius J. Reilly, Walker Percy
---
5/19/12 8:56 PM - Ignatius J. Reilly: I am at the moment writing a lengthy indictment against our century.
5/19/12 8:57 PM - Walker Percy: lol
```

---

## chat_mbox_converter.py

Extracts chat messages matching a search term (sender, recipient, or body) from a chats mbox into a readable text file.

```bash
python3 chat_mbox_converter.py <input.mbox> <output.txt> [--sender P] [--to P] [--subject P] [--body P]
```

**Example:**
```bash
python3 chat_mbox_converter.py chats_only.mbox results.txt --sender "ignatius@lsu.edu"
python3 chat_mbox_converter.py chats_only.mbox results.txt --sender "ignatius" --body "mongoloid"
```

**Output format:**
Same as `chat_threads.py`
---

## email_mbox_converter.py

Searches a Gmail mbox for emails matching a name or address (partial, case-insensitive) in From/To/CC headers and extracts them to a readable text file. Chats are excluded.

```bash
python3 email_mbox_converter.py <input.mbox> <output.txt> <search term>
```

**Output format:**
```
===
From: no-reply@levypants.com
To: ceo@abelmansdrygoods.com
Date: 5/19/12 8:56 PM
Subject: On proper geometry and theology
Body:
Mr. I. Abelman, Mongoloid, Esq.,

We have received via post your absurd comments about our trousers, the comments revealing, as they did, your total lack of contact with reality.
```

---

## find_email_addresses.py

Searches a Gmail mbox for emails matching a name or address and outputs a deduplicated list of matching addresses. Useful for identifying the exact address to use in other scripts. Chats are excluded.

```bash
python3 find_email_addresses.py <input.mbox> <search term>
```

**Example:**
```bash
python3 find_email_addresses.py gmail.mbox "ignatius"
```

**Output:**
```
ireilly3@lsu.edu <Ignatius J. Reilly>
ignatius@levypants.com <Customer Support>
```
