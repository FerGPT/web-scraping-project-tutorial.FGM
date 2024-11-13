import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pprint import pprint


########    Step 1: INSTALL DEPENDENCIES    ########
# I have personally installed all the "requirementes.txt" file #


print ("Step 2: DOWNLOADING THE HTML")

resource_url = "https://ycharts.com/companies/TSLA/revenues"

print ("\n- First of all, will select the resource to download from the designated webpage." "\n  In this case: https://ycharts.com/companies/TSLA/revenues")

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
response = requests.get(resource_url, headers=headers)

if response.status_code == 200:
    with open("revenues.html", "wb") as dataset:
        dataset.write(response.content) 
    print("\n  HTML content downloaded successfully !")
else:
    print(f"Request failed with status code: {response.status_code}")

response


#######    Step 3: TRANSFORMING THE HTML    ########

print ("Step 3: TRANSFORMING THE HTML")
   

# We transform the flat HTML into real HTML (structured and nested, tree-like)
 
with open("revenues.html", "w", encoding="utf-8") as dataset:
    dataset.write(response.text)

    # Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')
soup

tables = soup.find_all("table")
tables

# Filter the table that contains 'Revenue'
for table in tables:
    if "Date" in str(table):
        target_table = table
        break

# Create DataFrame from the found table
rows = target_table.find_all("tr")
data = []

for row in rows:
    cols = row.find_all("td")
    cols = [col.text.strip().replace("$", "").replace(",", "") for col in cols if col.text.strip()]
    if cols:
        data.append(cols)

# Convert to DataFrame
df = pd.DataFrame(data, columns=["Date", "Revenue"])

# Display more rows if needed
pd.set_option('display.max_rows', None)

print(df)



########    Step 5: STORING THE DATA IN QLITE    ########


connection = sqlite3.connect("Tesla.db")

connection

#cursor = connection.cursor()
#cursor.execute("""CREATE TABLE Revenue_1 (Date, Revenue)""")

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("financial_data.db")

# Store the DataFrame in the SQLite database
# If the table 'revenue_data' already exists, replace it
df.to_sql("revenue_data", conn, if_exists="replace", index=False)

# Commit and close the connection
conn.commit()
conn.close()

print("Data has been stored in SQLite database successfully.")


# Convert your DataFrame (df) into a list of tuples
#df_tuples = list(df.to_records(index=False))

# Display the first 5 tuples to check the result
#pprint(df_tuples[:25])

df_tuples = list(df.to_records(index=False))

# Display the first 5 tuples to check the result
pprint(df_tuples[:25])  # You can adjust the number of tuples as needed



########     6. DATA VISUALISATION     ########


# GRAPH 1 #

df['Date'] = pd.to_datetime(df['Date'])
df['Revenue'] = df['Revenue'].replace({'B': ''}, regex=True).astype('float')  # Example to handle billions formatting if needed
df = df.sort_values('Date')

# Plotting the data
fig, axis = plt.subplots(figsize=(10, 5))
sns.lineplot(data=df, x='Date', y='Revenue', ax=axis)

# Formatting the plot
axis.set_title("Tesla Revenue Over Time")
axis.set_xlabel("Date")
axis.set_ylabel("Revenue (Billions)")

plt.tight_layout()
plt.show()


# GRAPH 2 #

# Resample data to get quarterly accumulated revenue
df.set_index('Date', inplace=True)
quarterly_revenue = df['Revenue'].resample('Q').sum().reset_index()

# Plotting the quarterly accumulated revenue
plt.figure(figsize=(12, 6))
sns.barplot(data=quarterly_revenue, x='Date', y='Revenue', color='skyblue')
plt.title("Quarterly Accumulated Revenue")
plt.xlabel("Quarter")
plt.ylabel("Total Revenue (Billions)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# GRAPH 3 #

# Group data to get monthly average revenue
monthly_avg_revenue = df['Revenue'].resample('M').mean().reset_index()

# Plotting the monthly average revenue
plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_avg_revenue, x='Date', y='Revenue', marker='o', color='green')
plt.title("Monthly Average Revenue")
plt.xlabel("Date")
plt.ylabel("Average Revenue (Billions)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()