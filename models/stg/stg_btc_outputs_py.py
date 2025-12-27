import pandas
import simplejson


def model(dbt, session):

    # Configure the model materialization and required packages
    dbt.config(materialized="table", packages=["pandas", "simplejson"])

    # Load the staging table data into a pandas DataFrame
    df = dbt.ref("stg_btc").to_pandas()

    # Parse the 'OUTPUTS' column from JSON string to Python objects
    df["OUTPUTS"] = df["OUTPUTS"].apply(simplejson.loads)

    # Explode the 'OUTPUTS' list so each output gets its own row
    df_exploded = df.explode("OUTPUTS").reset_index(drop=True)

    # Normalize the JSON data in 'OUTPUTS' to extract 'address' and 'value' columns
    df_outputs = pandas.json_normalize(df_exploded["OUTPUTS"])[["address", "value"]]

    # Concatenate the exploded DataFrame (without original 'OUTPUTS') with the new columns
    df_final = pandas.concat([df_exploded.drop(columns="OUTPUTS"), df_outputs],axis=1)

    # Filter out rows where the address is null
    df_final = df_final[df_final["address"].notnull()]

    # Convert all column names to uppercase for consistency
    df_final.columns = [col.upper() for col in df_final.columns]

    # Return the final transformed DataFrame
    return df_final