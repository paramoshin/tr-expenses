from __future__ import annotations
from typing import *

import argparse
import csv
import json
import os
import re
from pathlib import Path

from utils import str_to_num


def parse_chat_history(
        history_path: Union[Path, str],
        allowed_users: Optional[List[int]] = None,
        exclude_messages: Optional[List[int]] = None,
) -> List[Tuple(str, str)]:
    try:
        with open(history_path, "r") as f:
            history = json.load(f)
    except Exception as e:
        raise ValueError("couldn't read file")

    if exclude_messages is None:
        exclude_messages = []

    messages = []
    for msg in history["messages"]:

        if ("from_id" in msg) & (not "forwarded_from" in msg):

            condition = msg["id"] not in exclude_messages
            if allowed_users is not None:
                condition = (condition & (msg["from_id"] in allowed_users))

            if not condition:
                continue

            if (type(msg["text"]) == str) & (msg["text"] != ""):
                messages.append((msg["date"], msg["text"]))

            elif (
                (type(msg["text"]) == list) & 
                (len(msg["text"]) == 2) 
            ):
                if msg["text"][0] == {"type": "bot_command", "text": "/add"}:
                    messages.append((msg["date"], msg["text"][1]))

    return messages


def get_amount(text: str) -> float:
    pattern = re.compile("(\+|-+)?(\d+(\,|\.)?\d*)")
    fixed_text = text.replace(" ", "").replace("\n", "").replace("--", "-")
    groups = pattern.findall(fixed_text)
    if groups:
        amount = 0
        for group in groups:
            if group[0] in ("", "+"):
                amount += str_to_num(group[1])
            else:
                amount -= str_to_num(group[1])
        return amount
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--path", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-u", "--allowed-users", nargs="+", type=int, default=None)
    parser.add_argument("-m", "--exclude-messages", nargs="+", type=int, default=None)

    args = parser.parse_args()

    messages = parse_chat_history(args.path, args.allowed_users, args.exclude_messages)
    
    with open(args.output, "w") as f:
        wrtr = csv.writer(f)

        for dt, text in messages:
            amount = get_amount(text)
            if amount is not None:
                wrtr.writerow((dt, amount))
        
    print("done")
