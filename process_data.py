import pandas as pd
import streamlit as st

def process_data(df, show_log=True):
    processed_df = df.copy()
    log_msgs = []
    # Combine 'Account Type' and 'Account Number' into 'Account Info', but do NOT drop the originals
    if 'Account Type' in processed_df.columns and 'Account Number' in processed_df.columns:
        processed_df['Account Info'] = processed_df['Account Type'].astype(str) + ' (' + processed_df['Account Number'].astype(str) + ')'
        log_msgs.append(("success", "'Account Info' column created in the format: Account Type (Account Number)."))
    else:
        log_msgs.append(("warning", "'Account Type' and/or 'Account Number' columns not found in the uploaded file."))

    # Clean 'Value' column: remove rows with non-numeric or zero values
    if 'Value' in processed_df.columns:
        processed_df['Value'] = pd.to_numeric(processed_df['Value'], errors='coerce')
        before_count = len(processed_df)
        processed_df = processed_df.dropna(subset=['Value'])
        processed_df = processed_df[processed_df['Value'] != 0]
        after_count = len(processed_df)
        log_msgs.append(("info", f"Removed {before_count - after_count} rows with non-numeric or zero 'Value'."))
    else:
        log_msgs.append(("warning", "'Value' column not found in the uploaded file."))

    # Update 'Asset Category' column: change 'U.S. Small Cap' to 'U.S. Equity'
    if 'Asset Category' in processed_df.columns:
        processed_df['Asset Category'] = processed_df['Asset Category'].replace('U.S. Small Cap', 'U.S. Equity')
        log_msgs.append(("info", "Replaced 'U.S. Small Cap' with 'U.S. Equity' in 'Asset Category' column."))
    else:
        log_msgs.append(("warning", "'Asset Category' column not found in the uploaded file."))

    # Sort by Asset Category priority
    if 'Asset Category' in processed_df.columns:
        priority = {
            'U.S. Equity': 1,
            "Int’l Equity": 2,
            'Fixed Income': 3,
            'MM, Cash & Equiv.': 4
        }
        processed_df['__sort_order'] = processed_df['Asset Category'].map(priority).fillna(99)
        processed_df = processed_df.sort_values(by='__sort_order').drop(columns='__sort_order').reset_index(drop=True)
        log_msgs.append(("info", "Sorted by Asset Category priority."))
    else:
        log_msgs.append(("warning", "'Asset Category' column not found in the uploaded file."))

    if show_log:
        with st.expander("Show Processing Log"):
            for msg_type, msg in log_msgs:
                if msg_type == "info":
                    st.info(msg)
                elif msg_type == "success":
                    st.success(msg)
                elif msg_type == "warning":
                    st.warning(msg)
    return processed_df
