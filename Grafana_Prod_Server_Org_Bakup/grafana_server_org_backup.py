
import requests
import os
import json
import shutil
from datetime import datetime


# Read config directly
with open("config.json", "r") as f:
    config = json.load(f)

    
# -----------------------------
# CONFIGURATION
# -----------------------------
GRAFANA_URL = config["grafana_url"]
USERNAME = config["username"]
PASSWORD = config["password"]
BACKUP_DIR = config["backup_dir"]

# -----------------------------
# UTILS
# -----------------------------

def make_dir(path):
    # If folder exists, delete it first
    if os.path.exists(path):
        shutil.rmtree(path)
    # Now create a fresh folder
    os.makedirs(path)

def get_orgs():
    url = f"{GRAFANA_URL}/api/orgs"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching orgs:", response.text)
        return []

def switch_org(org_id):
    url = f"{GRAFANA_URL}/api/user/using/{org_id}"
    response = requests.post(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return True
    else:
        print(f"Failed to switch to org {org_id}: {response.text}")
        return False



def get_folders():
    url = f"{GRAFANA_URL}/api/folders"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching folders:", response.text)
        return []

def get_dashboards(folder_id):
    url = f"{GRAFANA_URL}/api/search?folderIds={folder_id}&type=dash-db"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching dashboards for folder {folder_id}:", response.text)
        return []

def get_datasources():
    url = f"{GRAFANA_URL}/api/datasources"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching datasources:", response.text)
        return []

def backup_dashboard(dashboard_uid, folder_path):
    url = f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_uid}"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        dashboard = response.json()
        title = dashboard["dashboard"]["title"].replace(" ", "_")
        file_path = os.path.join(folder_path, f"{title}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dashboard, f, indent=2)
        print(f"Saved dashboard: {title}")
    else:
        print(f"Failed to get dashboard {dashboard_uid}: {response.status_code}")

def backup_datasource(ds, folder_path):
    uid = ds.get("uid", ds.get("name", "unknown")).replace(" ", "_")
    file_path = os.path.join(folder_path, f"{uid}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(ds, f, indent=2)
    print(f"Saved datasource: {uid}")


def zip_folder(folder_path):
    zip_path = shutil.make_archive(folder_path, 'zip', folder_path)
    print(f"Created ZIP: {zip_path}")

# -----------------------------
# MAIN BACKUP LOGIC
# -----------------------------
def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    make_dir(BACKUP_DIR)

    orgs = get_orgs()
    for org in orgs:
        org_name = org["name"].replace(" ", "_")
        org_id = org["id"]

        print(f"\nBacking up Org: {org['name']} (ID: {org_id})")

        if not switch_org(org_id):
            continue

        # ----------------------
        # Get only InfluxDB datasources
        datasources = [ds for ds in get_datasources() if ds.get("type") == "influxdb"]
        if not datasources:
            print(f"No InfluxDB datasource found in org {org['name']}")
            continue

        for ds in datasources:
            ds_uid = ds.get("uid", ds.get("name", "unknown")).replace(" ", "_")
            # Folder naming: ORGNAME_DATASOURCEUID_DATE
            org_ds_backup_dir = os.path.join(BACKUP_DIR, f"{org_name}_{ds_uid}_{date_str}")
            make_dir(org_ds_backup_dir)

            # Save datasource JSON
            backup_datasource(ds, org_ds_backup_dir)

            # Backup General dashboards
            general_backup_dir = os.path.join(org_ds_backup_dir, "General")
            make_dir(general_backup_dir)
            dashboards = get_dashboards(0)
            for dash in dashboards:
                backup_dashboard(dash["uid"], general_backup_dir)

            # Backup normal folders
            folders = get_folders()
            for folder in folders:
                folder_name = folder["title"].replace(" ", "_")
                folder_backup_dir = os.path.join(org_ds_backup_dir, folder_name)
                make_dir(folder_backup_dir)
                print(f"  Folder: {folder['title']}")

                dashboards = get_dashboards(folder["id"])
                for dash in dashboards:
                    backup_dashboard(dash["uid"], folder_backup_dir)

   # ZIP after backup complete
            zip_folder(org_ds_backup_dir)
     # Delete folder after zip
            shutil.rmtree(org_ds_backup_dir)


#unzip command use in bash : for f in *.zip; do mkdir -p "${f%.zip}" && unzip "$f" -d "${f%.zip}"; done



#unzip simple versoin for f in *.zip; do unzip "$f" -d "${f%.zip}"; done

if __name__ == "__main__":
    main()
