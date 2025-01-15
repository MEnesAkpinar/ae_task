# The Python scripts performs fuzzy matching and stores the results in te 'pre_fuzzy_result' table. It loads Snowflake credentials from the 'config.yml.

import snowflake.connector
from fuzzywuzzy import fuzz
from collections import defaultdict
import yaml
import os


def load_config():
    with open(os.path.join(os.path.dirname(__file__), '../config/config.yml'), 'r') as file:
        config = yaml.safe_load(file)
    return config['snowflake']

snowflake_config = load_config()


conn = snowflake.connector.connect(
    user=snowflake_config['user'],
    password=snowflake_config['password'],
    account=snowflake_config['account'],
    warehouse=snowflake_config['warehouse'],
    database=snowflake_config['database'],
    schema=snowflake_config['schema']
)


cursor = conn.cursor()
cursor.execute("""
    SELECT Account_UUID, Site_Name_Cleansed, Country_Name, Source_IDs
    FROM adp_workspaces.ae.pre_fuzzy_cleansed
""")
records = cursor.fetchall()


data = []
for record in records:
    account_uuid, site_name, country_name, source_ids = record
    data.append({
        "Account_UUID": account_uuid,
        "Site_Name_Cleansed": site_name,
        "Country_Name": country_name,
        "Source_IDs": source_ids
    })

matches = defaultdict(list)  # Store matches for each Account_UUID

for i in range(len(data)):
    for j in range(i + 1, len(data)):
        # Ensure records are from different sources
        if not set(data[i]["Source_IDs"]).intersection(set(data[j]["Source_IDs"])):
            # Compare Site_Name_Cleansed and Country_Name
            if data[i]["Country_Name"] == data[j]["Country_Name"]:
                similarity = fuzz.ratio(data[i]["Site_Name_Cleansed"], data[j]["Site_Name_Cleansed"])
                if similarity >= 80:  # Match threshold is 80%
                    matches[data[i]["Account_UUID"]].append(data[j]["Account_UUID"])
                    matches[data[j]["Account_UUID"]].append(data[i]["Account_UUID"])

aggregated_matches = []
for account_uuid, matched_uuids in matches.items():
    aggregated_matches.append((account_uuid, matched_uuids))

# Insert matched results into the pre_fuzzy_result table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS adp_workspaces.ae.pre_fuzzy_result (
        Account_UUID STRING,
        Matched_UUIDs ARRAY
    )
""")

for account_uuid, matched_uuids in aggregated_matches:
    cursor.execute("""
        INSERT INTO adp_workspaces.ae.pre_fuzzy_result (Account_UUID, Matched_UUIDs)
        VALUES (%s, %s)
    """, (account_uuid, matched_uuids))

conn.commit()
cursor.close()
conn.close()

print("Fuzzy matching completed and results stored in adp_workspaces.ae.pre_fuzzy_result.")



