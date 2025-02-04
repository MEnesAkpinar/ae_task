
{{
    config(
        materialized='table',
        schema='ae'
    )
}}

WITH source_data AS (
    SELECT
        Account_UUID,
        Site_Name,
        Parent_Account_Name,
        Country_Name,
        Source_ID
    FROM
        {{source('ae_task', 'sources_for_fuzzy')}}
)

SELECT
    Account_UUID,
    MAX(Site_Name) AS Site_Name,
    MAX(Parent_Account_Name) AS Parent_Account_Name,
    MAX(Country_Name) AS Country_Name,
    ARRAY_AGG(DISTINCT Source_ID) AS Source_IDs
FROM
    source_data
GROUP BY
    Account_UUID