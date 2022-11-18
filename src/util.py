# import library
import numpy as np
import pandas as pd
import pyodbc
import streamlit as st
from collections import Counter
from io import BytesIO


# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )


# Perform query.
# Uses st.experimental_memo, only rerun when the query changes or after 10 min.
@st.experimental_memo
def read_data(sql_query, _conn):
    return pd.read_sql_query(sql_query, _conn)


def format_func(x: object):
    m_type, m_value = x.split(": ")
    m_value_float = float(m_value)
    disp_val = f'{m_type}: {m_value_float / pow(10, 6):,.2f}'
    return disp_val


def derived_variables_calc(d):
    """

    :param dict d:
    :return: dict
    """

    d["Net Revenue"] = d["Nominal Income"] + d["Discounts"]  # discount is coming as negative values
    d["MACO"] = d["Net Revenue"] + d["Costs"]
    d["EBITDA"] = d["MACO"] + d["Expenses"]
    deductions = d["Depreciation Amortization"] + d["Cuentas Mayor"] + d["Inflationary Adjustments"] + d[
        "Other Expenses"]

    d["EBT"] = d["EBITDA"] + deductions
    d["PC"] = (d["EBT"] / d["Nominal Income"])
    return d


def results_df_creation(selected_data, adjusted_data):
    """
    https://stackoverflow.com/questions/30506219/is-there-a-counter-in-python-that-can-accumulate-negative-values
    :param selected_data:
    :param adjusted_data:
    :return: df
    """
    # create dummy dataframe with column and index names
    column_names = ["model values", "adjustments", "final values"]
    index_names = ["Beer Sales", "Discounts", "Net Revenue", "Costs", "MACO", "Expenses",
                   "EBITDA", "Depreciation Amortization", "Other Expenses",
                   "Cuentas Mayor", "Inflationary Adjustments", "EBT", "Nominal Income", "PC"]

    df = pd.DataFrame(index=index_names, columns=column_names)
    # calculate final values
    final = Counter()
    selected_counter = Counter(selected_data)
    adjusted_counter = Counter(adjusted_data)

    # sum; final= selected_data + adjusted_data
    final.update(selected_counter)
    final.update(adjusted_counter)

    # derive metrics
    selected_data = derived_variables_calc(selected_data)
    final = derived_variables_calc(final)

    # final df
    df.loc[:, "model values"] = pd.Series(selected_data)
    df.loc[:, "adjustments"] = pd.Series(adjusted_data)
    df.loc[:, "final values"] = pd.Series(final)

    return df


def to_excel(df):
    """

    :param df:
    :return: DataFrame
    """
    # format df output
    tmp_df = df.copy()

    # drivers
    driver_df = tmp_df.iloc[tmp_df.index != 'PC']
    pc_df = tmp_df.iloc[tmp_df.index == 'PC']

    # apply formatting
    # driver
    driver_df = driver_df.applymap(lambda x: f'{(0 if np.isnan(x) else x) / pow(10, 6):,.2f}')
    # pc
    pc_df = pc_df.applymap(lambda x: f'{(0 if np.isnan(x) else x):.2%}')

    # concat
    op_df = pd.concat([driver_df, pc_df])
    print(op_df)
    # output
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    op_df.to_excel(writer, index=True, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data
