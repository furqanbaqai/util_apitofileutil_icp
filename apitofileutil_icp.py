#!/usr/bin/env python3
"""Fetch numbered API pages with GET and save each response to a separate file."""

import argparse
import os
import sys
from datetime import datetime
from urllib import error, parse, request


def parse_params(param_items):
    """Convert key=value arguments to a dictionary, rejecting missing or empty keys.

    Values may contain '=' or be empty. Repeated keys use the last supplied value.
    """
    params = {}
    for item in param_items:
        if "=" not in item:
            raise ValueError(f"Invalid parameter '{item}'. Use key=value.")
        key, value = item.split("=", 1)
        if not key:
            raise ValueError(f"Invalid parameter '{item}'. Key cannot be empty.")
        params[key] = value
    return params


def add_timestamp_to_filename(path, timestamp, pgnum=1):
    """Insert a timestamp and page number before the path's final extension."""
    base, ext = os.path.splitext(path)
    return f"{base}_{timestamp}_{pgnum}{ext}"


def build_url(base_url, params):
    """Merge parameters into a URL, replacing existing values for matching keys.

    Preserve unrelated query values (including repeated and blank values) and
    the URL fragment. URL encoding handles special characters in keys and values.
    """
    url_parts = parse.urlsplit(base_url)
    existing = parse.parse_qs(url_parts.query, keep_blank_values=True)
    for key, value in params.items():
        existing[key] = [value]
    new_query = parse.urlencode(existing, doseq=True)
    return parse.urlunsplit(
        (
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            new_query,
            url_parts.fragment,
        )
    )


def fetch(url, transaction_key=None):
    """Return the GET response's status and raw bytes, optionally adding an API key.

    HTTPError and URLError propagate to the caller for command-line reporting.
    The response context manager closes the connection after the body is read.
    """
    headers = {}
    if transaction_key:
        headers["x-transaction-key"] = transaction_key
    req = request.Request(url, headers=headers, method="GET")
    with request.urlopen(req) as resp:
        status = resp.getcode()
        body = resp.read()
        return status, body


def main():
    """Parse CLI arguments and save pages 1 through max_pages, inclusive.

    Return 0 on completion, 2 for malformed key=value parameters, or 1 for a
    request failure or an unaccepted status. File-system errors propagate.
    """
    parser = argparse.ArgumentParser(
        description="Call a URL with GET and save the response to a timestamped file."
    )
    parser.add_argument(
        "url", help="Base URL to call, without or with query parameters."
    )
    parser.add_argument(
        "output_file",
        help="Path to the output file (timestamp will be appended before the extension).",
    )
    parser.add_argument(
        "transaction_key",
        type=str,
        help="x-transaction-key header value.",
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

    # Reject malformed query parameters before sending any network requests.
    try:
        params = parse_params(args.params)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    # Fetch a fixed number of pages; response contents do not signal completion.
    current_page = 1
    print(
        f"Fetching response from URL: {args.url}. Iterating through pages {args.max_pages}"
    )
    while current_page <= args.max_pages:
        print(f"Processing page {current_page} of {args.max_pages} ...")
        # Pagination always starts at 1, overriding any supplied page parameter.
        params["page"] = str(current_page)

        # Rebuild the URL each time so the query reflects the current page.
        final_url = build_url(args.url, params) if params else args.url

        try:
            status, body = fetch(final_url, args.transaction_key)
        except error.HTTPError as exc:
            print(f"HTTP error: {exc.code} {exc.reason}", file=sys.stderr)
            return 1
        except error.URLError as exc:
            print(f"Request failed: {exc.reason}", file=sys.stderr)
            return 1

        # Only these statuses are accepted for writing a response to disk.
        if status not in (200, 201):
            print(f"Unexpected status code: {status}", file=sys.stderr)
            return 1

        # Use local time for each response; the page suffix separates page files.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = add_timestamp_to_filename(args.output_file, timestamp, current_page)

        # Preserve the original bytes without assuming JSON, text, or an encoding.
        with open(out_path, "wb") as f:
            f.write(body)

        print(f"Saved response to {out_path}")
        current_page += 1

    return 0


if __name__ == "__main__":
    # Expose main's return value as the process exit code for shell automation.
    raise SystemExit(main())
