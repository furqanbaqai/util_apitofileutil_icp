#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import datetime
from urllib import parse, request, error


def parse_params(param_items):
    params = {}
    for item in param_items:
        if "=" not in item:
            raise ValueError(f"Invalid parameter '{item}'. Use key=value.")
        key, value = item.split("=", 1)
        if not key:
            raise ValueError(f"Invalid parameter '{item}'. Key cannot be empty.")
        params[key] = value
    return params


def add_timestamp_to_filename(path, timestamp):
    base, ext = os.path.splitext(path)
    return f"{base}_{timestamp}{ext}"


def build_url(base_url, params):
    url_parts = parse.urlsplit(base_url)
    existing = parse.parse_qs(url_parts.query, keep_blank_values=True)
    for key, value in params.items():
        existing[key] = [value]
    new_query = parse.urlencode(existing, doseq=True)
    return parse.urlunsplit(
        (url_parts.scheme, url_parts.netloc, url_parts.path, new_query, url_parts.fragment)
    )


def fetch(url):
    req = request.Request(url, method="GET")
    with request.urlopen(req) as resp:
        status = resp.getcode()
        body = resp.read()
        return status, body


def main():
    parser = argparse.ArgumentParser(
        description="Call a URL with GET and save the response to a timestamped file."
    )
    parser.add_argument("url", help="Base URL to call, without or with query parameters.")
    parser.add_argument(
        "output_file",
        help="Path to the output file (timestamp will be appended before the extension).",
    )
    parser.add_argument(
        "max_pages",
        type=int,
        default=10,
        help="Maximum number of pages to process.",
    )
    parser.add_argument(
        "params",
        nargs="*",
        help="Optional query parameters in key=value form (space-separated).",
    )
    args = parser.parse_args()

    # Loop through the params, increase the page number and 

    try:
        params = parse_params(args.params)        
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    final_url = build_url(args.url, params) if params else args.url

    try:
        status, body = fetch(final_url)
    except error.HTTPError as exc:
        print(f"HTTP error: {exc.code} {exc.reason}", file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"Request failed: {exc.reason}", file=sys.stderr)
        return 1

    if status not in (200, 201):
        print(f"Unexpected status code: {status}", file=sys.stderr)
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = add_timestamp_to_filename(args.output_file, timestamp)

    with open(out_path, "wb") as f:
        f.write(body)

    print(f"Saved response to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
