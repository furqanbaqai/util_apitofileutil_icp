# Introduction
Implemented a CLI utility that builds a GET URL with query params, calls it, and writes the response to a timestamped output file when the status is 200/201. Added argument parsing, URL/query handling, and safe filename timestamping in apitofileutil_icp.py.

# Details

apitofileutil_icp.py now accepts url, output_file, and optional key=value params.
Builds the final URL including existing query params, performs GET, and writes to output_file_YYYYMMDD_HHMMSS.ext on success.
Example
```
python util_apitofileutil_icp/apitofileutil_icp.py \
  "https://example.com/api" \
  "response.json" \
  foo=bar limit=10
```
Next steps (optional)

Run a quick manual call against a known endpoint to verify output.
Add a small README or usage note if this is for other users.

## Example Usage
Sample URL: https://restcountries.com/v3.1/all?fields=name,flags
```bash
python apitofileutil_icp.py \
  "https://restcountries.com/v3.1/all" \
  "response.json" \
  fields=name,flags
```
## Example Usage 2
Sample URL: https://api.github.com/repos/octocat/Spoon-Knife/issues?per_page=2&page=1
```bash
python apitofileutil_icp.py \
  "https://api.github.com/repos/octocat/Spoon-Knife/issues" \
  "response_git_.json" \
  10 \
  page=1 per_page=10

  python apitofileutil_icp.py \
  "https://api.github.com/repos/octocat/Spoon-Knife/issues" \
  output_file="response_git.json" \
  transaction_key \
  10 \
  page=1 per_page=10
```
 "https://restcountries.com/v3.1/all" "response.json" 1 transaction_key page=1 per_page=10

 # Instructions for creating a single binary
 ```python
 # From repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pyinstaller

# Build a single-file exe (no UPX compression)
pyinstaller --onefile --noupx --name apitofileutil_icp apitofileutil_icp.py

# Build a directory-based exe (no UPX compression)
pyinstaller --onedir --noupx --name apitofileutil_icp apitofileutil_icp.py

 ```
