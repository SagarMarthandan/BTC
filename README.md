# BTC dbt Project Documentation

This project is designed to process Bitcoin transaction data within a Snowflake environment using dbt. It handles data ingestion from raw sources, flattens complex nested structures, and produces analytical models to identify "Whale" activities.

---

## 1. Project Configuration

### `dbt_project.yml`
The core configuration file for the dbt project.
*   **Project Name:** `BTC`
*   **Profile:** Uses the `BTC` profile for connection settings.
*   **Model Paths:** Defines where dbt looks for models, seeds, macros, and tests.
*   **Marts Configuration:** Specifically configures models in the `marts` folder to materialize as tables and includes post-hooks for table commenting and versioned view creation.

---

## 2. Models (`/models`)

The models are organized into layers following dbt best practices: Staging and Marts.

### Staging Layer (`/models/stg`)
This layer handles the initial cleaning and transformation of raw source data.

*   **`stg_btc.sql`**
    *   **Materialization:** Incremental (Merge strategy).
    *   **Purpose:** Acts as the entry point for raw Bitcoin data from the `btc.btc_schema.btc` source.
    *   **Logic:** It uses a `HASH_KEY` as a unique identifier and incrementally loads new data based on the `BLOCK_TIMESTAMP`.

*   **`stg_btc_outputs.sql`**
    *   **Materialization:** Incremental (Append strategy).
    *   **Purpose:** Bitcoin transactions often contain multiple outputs in a nested format. This model flattens that data.
    *   **Logic:** It uses Snowflake's `LATERAL FLATTEN` on the `outputs` column to create a row for every unique address/value pair in a transaction.

*   **`stg_btc_transactions.sql`**
    *   **Materialization:** Ephemeral (CTE-based, not created in the DB).
    *   **Purpose:** Filters the flattened outputs to focus on standard transactions.
    *   **Logic:** It excludes "Coinbase" transactions (newly minted coins) to focus on peer-to-peer transfers.

### Marts Layer (`/models/marts`)
The analytical layer where business logic is applied.

*   **`whale_alerts.sql`**
    *   **Materialization:** Table.
    *   **Purpose:** Identifies "Whales"—addresses involved in high-value transactions.
    *   **Logic:** 
        *   Filters for transactions where the output value is greater than 10 BTC.
        *   Aggregates data by `output_address` to show total sent and transaction counts.
        *   Uses a custom macro to calculate the USD value of the BTC sent.
    *   **Versioning:** This model supports multiple versions (v1 and v2) as defined in `schema.yml`.

---

## 3. Seeds (`/seeds`)

Seeds are CSV files that dbt loads into your data warehouse as tables.

*   **`btc_usd_max.csv`**
    *   **Purpose:** Provides historical and current BTC to USD exchange rates.
    *   **Usage:** Referenced by the `convert_to_usd` macro to provide financial context to transaction volumes.

---

## 4. Macros (`/macros`)

Macros are reusable chunks of logic (like functions) written in Jinja and SQL.

*   **`btc_utils.sql`**
    *   **`convert_to_usd(column_name)`:** This macro takes a BTC value column and multiplies it by the latest price found in the `btc_usd_max` seed table for the current date.

---

## 5. Documentation & Metadata (`/models/schema.yml`)

This file defines the "contract" for the models, including testing and external exposures.

*   **Tests:**
    *   `HASH_KEY` in `stg_btc` is tested for `unique` and `not_null`.
    *   `stg_btc_outputs` includes a row count comparison against a Python-based model.
    *   `output_address` in `whale_alerts` uses a custom data test `assert_valid_btc_address`.
*   **Exposures:**
    *   **`btc_whale_alerts_exposure`:** Documents that the `whale_alerts` (v2) model is used in a Looker Studio dashboard for Bitcoin whale monitoring.

---

## 6. Project State (`/state`)

*   **`manifest.json`**
    *   A machine-generated file containing the full representation of the project's resources and their dependencies. It is used by dbt to understand the project structure and for state-based execution (e.g., `dbt build --state ...`).
