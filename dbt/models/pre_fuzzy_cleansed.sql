
{{
    config(
        materialized='table',
        schema='ae'
    )
}}

WITH cleansed_data AS (
    SELECT
        Account_UUID,
        UPPER(REGEXP_REPLACE(Site_Name, '[^\\w\\s]', '')) AS Site_Name_Cleansed,
        UPPER(REGEXP_REPLACE(Parent_Account_Name, '[^\\w\\s]', '')) AS Parent_Account_Name_Cleansed,
        Country_Name,
        Source_IDs
    FROM
        {{ ref('aggregate_data') }}
)

SELECT
    Account_UUID,
    Site_Name_Cleansed,
    Parent_Account_Name_Cleansed,
    Country_Name,
    Source_IDs
FROM
    cleansed_data