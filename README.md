* **GlobalProtect Version Tracker**

  * This repository maintains a JSON file with metadata about the latest available GlobalProtect client versions for Palo Alto Networks firewalls.

* **Overview**

  1. A local automation (not shipped here) does the heavy lifting:

     1. Connects via the GlobalProtect API or XML interface
     2. Pulls version info for both client installers
     3. Updates a local JSON file with that data
     4. Commits & pushes the changes back to this GitHub repo

* **Repository Contents**

  * `globalprotect_versions.json`

    * Machine-readable list of available GlobalProtect versions (see schema below)

* **Note**

  * We only track version metadata here.
  * The script that generates this file lives somewhere more top-secret (and not in this repo).

---

* **JSON Schema Definition**

  ```json
  {
    "version":      "string (e.g. '6.2.8-c317')",
    "size-kb":      "string (numeric, kilobytes)",
    "released-on":  "string (format: 'YYYY/MM/DD HH:mm:ss')",
    "latest":       "string ('yes' or 'no')",
    "sha256":       "string | null",
    "release-type": "string (either '', 'Base', or 'Preferred')"
  }
  ```

  * **version**

    * Version identifier, including build or patch suffix
  * **size-kb**

    * Package size in KB (as a string)
  * **released-on**

    * Timestamp when released
  * **latest**

    * Flag marking the newest drop
  * **sha256**

    * Checksum for integrity (nullable if unavailable)
  * **release-type**

    * Release classification: empty string for regular, "Base" for core builds, or "Preferred" for recommended builds

---

* **JSON Example**

  ```json
  [
    {
      "version":      "6.2.8-c317",
      "size-kb":      "253936",
      "released-on":  "2025/09/09 09:00:09",
      "latest":       "no",
      "sha256":       "a62529aa4656453c7914bf367152e611c90e6f23cb6603e6a49b4d8f57bd321f",
      "release-type": ""
    },
    {
      "version":      "6.2.8-c263",
      "size-kb":      "253288",
      "released-on":  "2025/07/17 07:35:16",
      "latest":       "no",
      "sha256":       "f3cd71c1906a4de67f98f2487a4b4056fce979ab8f2e2cf50575bb2c56422b93",
      "release-type": "Preferred"
    },
    {
      "version":      "6.3.0",
      "size-kb":      "231471",
      "released-on":  "2024/06/13 10:50:28",
      "latest":       "no",
      "sha256":       "67a83ff5206d5b4a2aaf13bce3212de270cabe6204a4df1561c35aa4c1bc0f44",
      "release-type": "Base"
    }
  ]
  ```

---

* **Example Usage**

  1. Consume this JSON in your CI/CD, monitoring scripts, or just your morning coffee ritual:

     ```powershell
     # Load JSON
     $gpVersions = Get-Content -Raw -Path '.\globalprotect_versions.json' | ConvertFrom-Json

     # Get the Preferred build if available, else latest
     $preferred = $gpVersions |
       Where-Object { $_."release-type" -eq 'Preferred' }

     if ($preferred) {
       $chosen = $preferred
     } else {
       $chosen = $gpVersions | Where-Object { $_.latest -eq 'yes' }
     }

     Write-Host "Selected GlobalProtect build is $($chosen.version)"
     ```

---

* **Validation & Integrity**

  1. Ensure each entry has all required fields and correct data types.
  2. If `sha256` is provided, verify the installer/image matches.
  3. Use tools like:

     * `jq`
     * `ajv`
     * PowerShell’s `Get-FileHash`

---

* **Automated endoflife.date Updates**

  A GitHub Actions workflow automatically creates pull requests to update [endoflife.date](https://github.com/endoflife-date/endoflife.date) whenever new GlobalProtect versions are pushed to this repository.

  1. On every push to `GlobalProtectVersions.json`, the workflow runs `.github/scripts/update_gp_endoflife.py`
  2. The script compares versions in the JSON with the current state of [`products/pan-gp.md`](https://github.com/endoflife-date/endoflife.date/blob/master/products/pan-gp.md) in the upstream repository
  3. If a newer version is found for any release cycle, and no open `[pan-gp]` PR already exists, it creates a PR with the updated version and release date
  4. If an open PR already exists, it skips to avoid duplicates

  * **Manual trigger**

    ```bash
    gh workflow run update-endoflife.yml --repo mrjcap/globalprotect-versions
    ```

  * **Required secret**

    | Secret | Scope | Purpose |
    |---|---|---|
    | `ENDOFLIFE_PAT` | `public_repo` | Push to fork and create PRs against upstream |

> Kept up to date for clear version visibility—so you can automate rolls, alerts, and avoid nasty surprises. Stay ahead, stay protected!
