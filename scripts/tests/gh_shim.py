"""Stand-in for the gh CLI in the release rehearsal: forwards its arguments to the loopback fake API."""

import json
import os
import sys
from urllib.request import Request, urlopen


def main():
    request = Request(
        os.environ["GITHUB_API_URL"] + "/__gh", method="POST",
        data=json.dumps({"args": sys.argv[1:], "cwd": os.getcwd()}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=30) as response:
        result = json.loads(response.read())
    sys.stdout.buffer.write(result["stdout"].encode("utf-8"))
    sys.stderr.buffer.write(result["stderr"].encode("utf-8"))
    return result["code"]


if __name__ == "__main__":
    raise SystemExit(main())
