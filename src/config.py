# sql query to pull data *
# https://stackoverflow.com/questions/5243596/python-sql-query-string-formatting
from datetime import datetime

COUNTRY = 'MEXICO'
DLTDT = datetime.now(tz=None).strftime("%Y-%m-%d")
DLTTM = datetime.now(tz=None).strftime("%H-%M-%S")

SQL_QRY = ("select "
               "src.country, src.society, src.business_unity, src.year, src.month, "
               "src.component, isnull(src.forecast_number,0.00) as forecast_number, "
               "src.model_type,	src.le "
           "from "
                "abi_stg.mx_tax_prof_coef_results src "
           "inner join "
                "( "
                   "select "
                       "society, component, model_type, le, max(dltdt) as max_load_dt, max(dlttm) as max_load_tm "
                       "from "
                       "abi_stg.mx_tax_prof_coef_results "
                       # "where "
                       # "month(dltdt) = month(getdate()) "
                       "group by "
                       "society, component, model_type, le "
               ") dest "
           "on "
               "src.society = dest.society "
               "and src.component = dest.component "
               "and src.model_type = dest.model_type "
               "and src.le = dest.le "
               "and src.dltdt = dest.max_load_dt "
               "and src.dlttm = dest.max_load_tm ")
