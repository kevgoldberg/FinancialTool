import streamlit as st
import pandas as pd
from process_data import process_data
from data_upload import upload_data

def main():
    st.set_page_config(page_title="Finance Tool", layout="wide")
    st.title("📁 Personal Finance File Viewer")
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        </style>
        <div style='display: flex; justify-content: flex-start;'>
            <form action="#" method="post" enctype="multipart/form-data">
                <label for="file-upload" class="custom-file-upload">
                    <span style='font-size:16px; font-weight:500; color:#4CAF50;'>
                        <i class="fa fa-upload"></i> Upload File
                    </span>
                </label>
            </form>
        </div>
    """, unsafe_allow_html=True)

    df, uploaded_file = upload_data()
    if uploaded_file and df is not None:
        tab1, tab2, tab3 = st.tabs(["Orion Data", "Processed Data", "Current Portfolio"])
        with tab1:
            st.success("File uploaded successfully! Here's a preview:")
            st.dataframe(df)
        with tab2:
            processed_df = process_data(df, show_log=True)  # Show log here
            st.dataframe(processed_df)
        with tab3:
            processed_df = process_data(df, show_log=False)
            from current_portfolio import create_aggrid_data
            from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, JsCode
            st.subheader(":bar_chart: Current Portfolio - Interactive Pivot Table")
            aggrid_data = create_aggrid_data(processed_df)
            gb = GridOptionsBuilder.from_dataframe(aggrid_data)
            gb.configure_column("Asset Category", rowGroup=True, hide=True, header_name="Asset Category")
            gb.configure_column("Name", rowGroup=True, hide=True, header_name="Security Name")
            gb.configure_column("Ticker", rowGroup=True, hide=True, header_name="Ticker")
            gb.configure_column("Custodian", pivot=True, hide=True, header_name="Custodian")
            gb.configure_column("Account Type", pivot=True, hide=True, header_name="Account Type")
            gb.configure_column("Account Number", pivot=True, hide=True, header_name="Account Number")
            gb.configure_column("Value", aggFunc="sum", type=["numericColumn","numberColumnFilter","customNumericFormat"],
                               valueFormatter=JsCode('''function(params) {
                                   if(params.value === undefined || params.value === null || params.value === "") return "";
                                   return "$" + Number(params.value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
                               }'''),
                               header_name="Value ($)")
            gb.configure_side_bar()
            gb.configure_grid_options(pivotMode=True, domLayout='autoHeight', suppressAggFuncInHeader=True)
            gridOptions = gb.build()
            AgGrid(
                aggrid_data,
                gridOptions=gridOptions,
                data_return_mode=DataReturnMode.AS_INPUT,
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                theme='alpine',
                height=600,
                width='100%'
            )

if __name__ == "__main__":
    main()
