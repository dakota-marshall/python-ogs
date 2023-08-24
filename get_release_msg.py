#!/usr/bin/env python3
import re

regex = r"## \[\d+\.\d+\.\d+\][\s\S]*?(?=(^#{2} \[))"

# Open CHANGELOG.md
with open("CHANGELOG.md", "r") as file:
    test_str = file.read()

match = re.search(regex, test_str, re.MULTILINE)

print(match.group(0))