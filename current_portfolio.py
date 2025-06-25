import pandas as pd

def create_current_portfolio_pivot(df):
    """
    Build a pivot of your current portfolio where:
      - Rows: Asset Category, Name, Ticker
      - Columns: Custodian | Account Info
      - Values: Sum of Value
      - NO rows where you have zero in every single cell
      - Custom ordering of Asset Category
    """
    # 1) Drop any records missing required info
    df = df.dropna(subset=[
        "Asset Category", "Name", "Ticker",
        "Custodian", "Account Info", "Value"
    ]).copy()

    # 2) Pre-aggregate & keep only truly non-zero holdings
    df = (
        df
        .groupby(
            ["Asset Category", "Name", "Ticker", "Custodian", "Account Info"],
            as_index=False
        )["Value"]
        .sum()
    )
    df = df[df["Value"] != 0]   # <-- remove any zero-sum groups

    # 3) Enforce your custom category sort
    asset_order = ["U.S. Equity", "Int'l Equity", "Fixed Income", "MM, Cash & Equiv."]
    present = [c for c in asset_order if c in df["Asset Category"].unique()]
    rest    = sorted(set(df["Asset Category"]) - set(present))
    df["Asset Category"] = pd.Categorical(
        df["Asset Category"],
        categories=present + rest,
        ordered=True
    )

    # 4) Pivot
    pivot = df.pivot_table(
        index=["Asset Category", "Name", "Ticker"],
        columns=["Custodian", "Account Info"],
        values="Value",
        aggfunc="sum",
        fill_value=None  # Do not fill with 0s
    )

    # 5) Drop any rows that are still all zeros or NaN (just in case)
    pivot = pivot.loc[(pivot.sum(axis=1, skipna=True) != 0) & (~pivot.isna().all(axis=1))]

    # 6) Flatten the column MultiIndex for AgGrid compatibility
    pivot.columns = [
        f"{cust} | {acct}" if pd.notna(cust) and pd.notna(acct) else str(cust)
        for cust, acct in pivot.columns
    ]

    # 7) Replace 0s and NaN with blank (empty string)
    pivot = pivot.fillna("").replace(0, "")

    return pivot

def create_aggrid_data(df):
    """
    Create data structure suitable for AgGrid interactive pivot table
    """
    # Just return the processed data without pivoting for AgGrid to handle
    df = df.dropna(subset=[
        "Asset Category", "Name", "Ticker",
        "Custodian", "Account Info", "Value"
    ]).copy()

    # Pre-aggregate & keep only truly non-zero holdings
    df = (
        df
        .groupby(
            ["Asset Category", "Name", "Ticker", "Custodian", "Account Info"],
            as_index=False
        )["Value"]
        .sum()
    )
    df = df[df["Value"] != 0]

    # Enforce your custom category sort
    asset_order = ["U.S. Equity", "Int'l Equity", "Fixed Income", "MM, Cash & Equiv."]
    present = [c for c in asset_order if c in df["Asset Category"].unique()]
    rest = sorted(set(df["Asset Category"]) - set(present))
    df["Asset Category"] = pd.Categorical(
        df["Asset Category"],
        categories=present + rest,
        ordered=True
    )
    
    return df.sort_values("Asset Category")
