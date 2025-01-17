import snowflake.connector
from fuzzywuzzy import fuzz
from collections import defaultdict
import os


def fuzzy_match():
    

    # Get Snowflake credentials from environment variables
    snowflake_config = {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    }

    # Connect to Snowflake
    try:

        conn = snowflake.connector.connect(
            user=snowflake_config["user"],
            password=snowflake_config["password"],
            account=snowflake_config["account"],
            warehouse=snowflake_config["warehouse"],
            database=snowflake_config["database"],
            schema=snowflake_config["schema"]
        )


        # Fetch data from the pre_fuzzy_cleansed table
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Account_UUID, Site_Name_Cleansed, Country_Name, Source_IDs
            FROM adp_workspaces.ae.pre_fuzzy_cleansed
        """)
        records = cursor.fetchall()

        # Prepare data for fuzzy matching
        data = []
        for record in records:
            account_uuid, site_name, country_name, source_ids = record
            data.append({
                "Account_UUID": account_uuid,
                "Site_Name_Cleansed": site_name,
                "Country_Name": country_name,
                "Source_IDs": source_ids
            })

        # Perform fuzzy matching
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

        # Aggregate matches at the unique Account_UUID level
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

        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        print("Fuzzy matching completed and results stored in adp_workspaces.ae.pre_fuzzy_result.")

    except:
        print("Error..")    