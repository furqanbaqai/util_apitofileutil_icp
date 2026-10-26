# API to File Utility

A Python command-line utility that fetches numbered API pages using HTTP GET and saves each successful response to a timestamped file. Responses are saved as raw bytes, so the utility can store JSON, text, or other response formats.

## Requirements

- Python 3.6 or later.
- Network access to the API endpoint.
- An existing, writable output directory.

The script uses only the Python standard library; no packages need to be installed to run it. Run the commands below from the repository directory.

## Usage

```text
python apitofileutil_icp.py URL OUTPUT_FILE TRANSACTION_KEY MAX_PAGES [key=value ...]
```

| Argument | Description |
| --- | --- |
| `URL` | API URL, optionally including existing query parameters. |
| `OUTPUT_FILE` | Output path, such as `response.json`. A timestamp and page number are inserted before the final extension. |
| `TRANSACTION_KEY` | Value sent in the `x-transaction-key` header. This positional argument is required. An empty string omits the header when the shell passes it through. |
| `MAX_PAGES` | Required integer specifying how many pages to request, starting at page 1. Supply a positive value to fetch data; zero or negative values produce no requests or files. |
| `key=value` | Optional, space-separated query parameters. Quote an entire argument if its value contains spaces. |

### Argument order and validation

The first four arguments are **required positional arguments**, in this exact order:

| Position | Parser name | Type | Example |
| --- | --- | --- | --- |
| 1 | `url` | String | `"https://example.com/api/items"` |
| 2 | `output_file` | File path string | `"response.json"` |
| 3 | `transaction_key` | String | `"YOUR_TRANSACTION_KEY"` |
| 4 | `max_pages` | Integer | `3` |
| 5 onward | `params` | Zero or more `key=value` strings | `"limit=10" "status=active"` |

Although the source sets `default=10` for `max_pages`, argparse still requires this positional argument because it has no optional `nargs` setting. Always supply the page count explicitly.

Use a plain output filename in position 2. For example, `output_file=response.json` is treated as a literal filename, not a named option. The script does not define `--url`, `--output-file`, `--transaction-key`, or `--max-pages` flags. Its only built-in option is `-h` / `--help`.

Missing required arguments and non-integer page counts cause an argument-parsing error before any request is made. Query arguments without `=` (such as `limit`) or with an empty key (such as `=10`) also fail before making requests. The URL and output path are not validated by argparse; problems with them surface when requesting or writing files.

Display built-in help:

```powershell
python apitofileutil_icp.py --help
```

### Fetch without additional query parameters

Only the four required positional arguments are needed. The script still appends `page=1`:

```powershell
python apitofileutil_icp.py "https://example.com/api/items" "response.json" "YOUR_TRANSACTION_KEY" 1
```

### Fetch one page

Replace the example URL and transaction key with your API's values:

```powershell
python apitofileutil_icp.py "https://example.com/api/items" "response.json" "YOUR_TRANSACTION_KEY" 1 "limit=10"
```

### Fetch multiple pages

```powershell
python apitofileutil_icp.py "https://example.com/api/items?status=active" "response.json" "YOUR_TRANSACTION_KEY" 3 "limit=10" "category=office supplies"
```

This requests pages 1, 2, and 3 and creates files such as:

```text
response_20261026_143015_1.json
response_20261026_143016_2.json
response_20261026_143017_3.json
```

The timestamp uses the machine's local time and is generated separately for each response. The output directory is preserved. Existing files with the same generated name are overwritten.

### Override existing query parameters

```powershell
python apitofileutil_icp.py "https://example.com/api/items?status=inactive&page=9" "response.json" "YOUR_TRANSACTION_KEY" 1 "status=active" "filter=" "expression=a=b"
```

The request uses `status=active`, `page=1`, an empty `filter` value, and the value `a=b` for `expression`. Values are URL-encoded automatically. Supplying `"page=9"` as an additional argument would also be overridden by the script's page counter.

### Call an API that does not require a transaction key

The key argument must still occupy position 3. For shells that preserve empty arguments, pass an empty string. For example, in Bash:

```bash
python apitofileutil_icp.py "https://example.com/api/items" "response.json" "" 1
```

An empty key omits the `x-transaction-key` header. Empty-argument handling varies between PowerShell versions and native-command argument modes; use a shell that preserves the empty argument, such as Bash, for this example.

## Request and output behavior

- Additional query parameters replace matching parameters already present in the URL. Unrelated parameters are preserved.
- Repeated command-line keys use the last supplied value. Empty values and values containing `=` are supported; empty keys are rejected.
- The script controls the `page` parameter, overriding any page value in the URL or command-line parameters.
- Pagination runs through `MAX_PAGES` unless an error occurs. Empty responses and pagination metadata do not stop the loop.
- Only HTTP status codes `200` and `201` are accepted for saving a response.
- Response bytes are written unchanged, without decoding or JSON formatting. Each response is read fully into memory before writing.
- Requests run sequentially. There is no retry logic or explicitly configured request timeout.
- On a request failure, processing stops and previously saved files remain.

## Exit codes and errors

| Code | Meaning |
| --- | --- |
| `0` | Processing completed. This also applies when `MAX_PAGES` is zero or negative. |
| `1` | HTTP/network failure or a response status other than `200` or `201`. |
| `2` | Invalid command-line arguments or malformed `key=value` parameters. |

Request and parameter errors are printed to standard error. File-system errors, such as a missing output directory or insufficient write permissions, propagate as Python exceptions.

## Code overview

Each function has a docstring describing its role and relevant behavior.

| Function | Responsibility |
| --- | --- |
| `parse_params` | Validate query arguments and convert them into a dictionary. |
| `add_timestamp_to_filename` | Insert the timestamp and page number before the final file extension. |
| `build_url` | Merge and encode query parameters while preserving other URL components. |
| `fetch` | Perform a GET request with the optional transaction header and return the status and raw response bytes. |
| `main` | Parse CLI arguments, iterate through pages, handle request errors, and save responses. |

## Build a Windows executable

PyInstaller is required only for packaging. In PowerShell, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pyinstaller
```

Build a single executable:

```powershell
pyinstaller --onefile --noupx --name apitofileutil_icp apitofileutil_icp.py
```

The executable is written to `dist\apitofileutil_icp.exe`.

Alternatively, build a directory containing the executable and its dependencies:

```powershell
pyinstaller --onedir --noupx --name apitofileutil_icp apitofileutil_icp.py
```

The directory is written to `dist\apitofileutil_icp`. Use the same arguments as the Python script:

```powershell
.\dist\apitofileutil_icp.exe "https://example.com/api/items" "response.json" "YOUR_TRANSACTION_KEY" 3 "limit=10"
```
