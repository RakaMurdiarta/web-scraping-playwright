import connectorx as cx
import os

# Harus menggunakan relative path
path = os.getcwd()

# relative path
join_path = os.path.join(path, "warehouse-370706-8ad8207bcee6.json")

authentication_file_path = join_path.replace("\\", "/")

conn = "bigquery://" + authentication_file_path  # connection token
print(conn)
query = "SELECT * FROM `warehouse-370706.user.test`"  # query string
df = cx.read_sql(conn, query)
print(df)
