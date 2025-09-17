* **GlobalProtect Version Tracker**

  * This repository maintains a JSON file with metadata about the latest available GlobalProtect client and gateway versions for Palo Alto Networks.

* **Overview**

  1. A local automation (not shipped here) does the heavy lifting:

     1. Connects via the GlobalProtect API or XML interface
     2. Pulls version info for both client installers and gateway firmware
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
    "component": "string (e.g. 'client-win', 'gateway-firmware')",
    "version":   "string (e.g. '5.3.2')",
    "size-kb":   "string (numeric, kilobytes)",
    "released-on": "string (format: 'YYYY/MM/DD HH:mm:ss')",
    "latest":    "string ('yes' or 'no')",
    "sha256":    "string | null"
  }
  ```

  * **component**

    * Which piece—GlobalProtect client for Windows/Mac/Linux or gateway firmware
  * **version**

    * Version identifier
  * **size-kb**

    * Package size in KB (as a string)
  * **released-on**

    * Timestamp when released
  * **latest**

    * Flag marking the newest drop
  * **sha256**

    * Checksum for integrity (nullable if we couldn’t grab it)

---

* **JSON Example**

  ```json
  [
    {
      "component":    "client-win",
      "version":      "5.3.2",
      "size-kb":      "452312",
      "released-on":  "2025/08/20 14:22:10",
      "latest":       "yes",
      "sha256":       "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef"
    },
    {
      "component":    "gateway-firmware",
      "version":      "10.2.1",
      "size-kb":      "1120456",
      "released-on":  "2025/07/15 09:30:05",
      "latest":       "no",
      "sha256":       null
    }
  ]
  ```

---

* **Example Usage**

  1. Consume this JSON in your CI/CD, monitoring scripts, or just your morning coffee ritual:

     ```powershell
     # Load JSON
     $gpVersions = Get-Content -Raw -Path '.\globalprotect_versions.json' | ConvertFrom-Json

     # Pick the latest client build
     $latestClient = $gpVersions |
       Where-Object {
         $_.component -eq 'client-win' -and
         $_.latest    -eq 'yes'
       }

     Write-Host "Latest GlobalProtect Windows client is $($latestClient.version)"
     ```

---

* **Validation & Integrity**

  1. Make sure every entry has all required fields and correct data types.
  2. If `sha256` is provided, verify the installer/image matches.
  3. Use tools like:

     * `jq`
     * `ajv`
     * PowerShell’s `Test-FileHash`

> Kept up to date for clear version visibility—so you can automate rolls, alerts, and avoid nasty surprises. Stay ahead, stay protected!
