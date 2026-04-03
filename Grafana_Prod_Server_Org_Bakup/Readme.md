# Grafana Backup Script

## Overview

This Python script automates the backup of **Grafana dashboards** and **InfluxDB datasources** for all organizations in a Grafana instance.  
It retrieves dashboards from the **General folder** and any other folders, saves them as **JSON files**, and generates **ZIP archives** per organization and datasource.

---

## Features

- Backups for **all Grafana organizations** (multi-org support).
- Supports **InfluxDB datasources** only.
- Creates **JSON backups** for datasources and dashboards.
- Saves dashboards from **General folder** and other folders.
- Generates **ZIP files** for easy storage or migration.
- Automatically **cleans up** intermediate backup folders after zipping.

---

## Requirements

- Python 3.8+
- Python packages:
  - `requests`
- Grafana **Admin credentials**.
- Local folder to save backups.

---

## Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd grafana-backup

2.Install required packages:
pip install requests

##Configuration

Create a config.json file in the same folder as the script with the following structure:

{
  "grafana_url": "http://localhost:3000",
  "username": "admin",
  "password": "#Trguser1",
  "backup_dir": "./grafana_backup_test_server"
}

/* Key	Description
grafana_url  	URL of the Grafana server
username	    Admin username
password	    Admin password
backup_dir	  Local folder path for saving backups   */

Usage

Run the backup script:
-----------------------

python3 grafana_backup.py

The script will:

1.Create the backup folder if it does not exist.
2.Fetch all organizations from Grafana.
3.Switch to each organization.
4.Backup InfluxDB datasources and dashboards.
5.Create ZIP archives for each org-datasource combination.
6.Delete the intermediate unzipped folder to save space.

Folder Structure Example

After running the script, the folder structure will be:

grafana_backup_test_server/
│
├─ Org1_InfluxDB01_2026-04-03.zip
├─ Org2_InfluxDB02_2026-04-03.zip
│
# Inside ZIP example:
Org1_InfluxDB01_2026-04-03/
│
├─ General/
│   ├─ Dashboard1.json
│   └─ Dashboard2.json
├─ FolderA/
│   ├─ Dashboard3.json
│   └─ Dashboard4.json
└─ InfluxDB01.json  # Datasource backup

Create folder and unzip simultaneously:
-------------------------------------
for f in *.zip; do mkdir -p "${f%.zip}" && unzip "$f" -d "${f%.zip}"; done
Simple unzip into folder with the same name:
--------------------------------------------
for f in *.zip; do unzip "$f" -d "${f%.zip}"; done


Notes
Only InfluxDB datasources are backed up.
Dashboards are backed up per folder.
ZIP files are named as:
ORGNAME_DATASOURCEUID_YYYY-MM-DD.zip
Ensure the Grafana user has Admin privileges to access all organizations and dashboards.

License:
-------------

This project is released under the MIT License.

Contact:
-------------

For any issues or questions, please contact the repository owner or your DevOps team.



ASCII Workflow Diagram:
---------------------------


           +----------------+
           |   Grafana      |
           |   Server       |
           +----------------+
                  |
                  v
           +----------------+
           | Get all Orgs   |
           +----------------+
                  |
                  v
        +---------------------+
        | Switch to Org       |
        +---------------------+
                  |
                  v
        +---------------------+
        | Get InfluxDB        |
        | Datasources         |
        +---------------------+
                  |
                  v
        +---------------------+
        | For each Datasource |
        +---------------------+
                  |
                  v
       +-------------------------+
       | Create Backup Folder    |
       | ORG_DS_DATE             |
       +-------------------------+
                  |
        -------------------------
        |                       |
        v                       v
+-----------------+       +-----------------+
| Backup Datasource|      | Backup Dashboards|
+-----------------+       +-----------------+
                              |
            -------------------------------
            |                              |
            v                              v
      General Folder                  Other Folders
      Dashboards                      Dashboards
            |                              |
            -------------------------------
                  |
                  v
           +----------------+
           | ZIP Folder     |
           +----------------+
                  |
                  v
           +----------------+
           | Delete Temp    |
           | Folder         |
           +----------------+



