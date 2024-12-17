import mysql.connector
import datetime
import logging
import os

# from dotenv import load_dotenv
# load_dotenv()

formatter = logging.Formatter('[%(levelname)s] %(message)s')
log = logging.getLogger()
log.setLevel("INFO")

def convert_to_date_string(data):
    if isinstance(data, datetime.date):  # Check if it's a datetime.date object
        return data.strftime('%Y-%m-%d')
    else:
        return data  #



class Connection:
    def __init__(self, user, password, host, port, charset):
        try:
            self.cnx = mysql.connector.connect(
                user=user,
                password=password,
                host=host,
                database=os.getenv('DB_NAME'),
                port=port,
                charset=charset
            )
        except mysql.connector.Error as err:
            log.error("Connection to MySQL db could not be established")
            log.error(err)
            self.cnx = None

    def insert(self, table, json_data, batch_size=1000, mode='single'):
        log.info(f"Trying to insert records into table {table}")
        cursor = self.cnx.cursor()  # Get cursor from existing connection
        if table == 'activity':
            cursor.execute("SET NAMES utf8mb4;")
        if mode == 'single':
            try:

                # Construct the SQL query for bulk insert


                # Extract column names and values from the JSON data
                columns = ', '.join(json_data.keys())
                values = ', '.join(['%s'] * len(json_data))

                # Construct the SQL INSERT query
                query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

                # Execute the query with the JSON values
                cursor.execute(query, tuple(json_data.values()))

                # Commit the changes to the database
                self.cnx.commit()

                log.info("Data inserted successfully")

            except mysql.connector.Error as err:
                log.error(f"Error: {err}")
                self.cnx.rollback()  # Rollback changes in case of an error

        if mode == 'many':
            if len(json_data) > 0:
                try:

                    # Construct the SQL query for bulk insert
                    columns = json_data[0].keys()  # Assuming all objects have the same structure
                    query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(['%s'] * len(columns))})"

                    # Process data in batches
                    for i in range(0, len(json_data), batch_size):
                        batch_data = json_data[i:i + batch_size]

                        # Convert batch data to tuples for bulk insertion
                        data_tuples = [tuple(data[col] for col in columns) for data in batch_data]

                        # Execute the bulk insert for the batch
                        cursor.executemany(query, data_tuples)

                        # Commit the changes for the batch
                        self.cnx.commit()

                        log.info(f"Successfully inserted {len(batch_data)} rows (batch {i // batch_size + 1}) into the table {table}.")

                except mysql.connector.Error as err:
                    log.error(f"Error: {err}")
                    self.cnx.rollback()  # Rollback changes in case of an error

    def get_all(self, table, order_by='id', order_by_type='asc', type='first'):
        try:
            results = {}
            cursor = self.cnx.cursor()  # Get cursor from existing connection
            if type == 'all':
                query = f"SELECT * FROM {table} ORDER BY {order_by} {order_by_type}"
            elif type == 'first':
                query = f"SELECT * FROM {table} ORDER BY {order_by} {order_by_type}"
            else:
                return []
            cursor.execute(query)
            data = cursor.fetchall()

            if type == 'all':
                return data
            elif type == 'first':
                return data[0]


        except mysql.connector.Error as err:
            log.error(f"Error: {err}")


    def update(self, table='', json_data=None, record_id='id', mode='single', unique_column='id', custom=''):
        cursor = self.cnx.cursor()  # Get cursor from existing connection

        if mode == 'single':
            log.info(f"Trying to update record with {unique_column}={record_id} in table {table}")
            try:

                if custom != '':
                    query = custom
                    cursor.execute(query)
                else:
                    # Construct the SET clause for the UPDATE query
                    set_clause = ', '.join([f"{key} = %s" for key in json_data.keys()])

                    # Build the UPDATE query
                    query = f"UPDATE {table} SET {set_clause} WHERE {unique_column} = %s"

                # Execute the query with the updated values and the record ID
                    cursor.execute(query, tuple(json_data.values()) + (record_id,))

                # Commit the changes to the database
                self.cnx.commit()

                log.info("Record updated successfully!")

            except mysql.connector.Error as err:
                log.error(f"Error updating record: {err}")


    def remove_duplicates(self, table, grouping):
        try:
            results = {}
            cursor = self.cnx.cursor()  # Get cursor from existing connection
            query = f"SELECT * FROM {table} GROUP BY {grouping} HAVING count(*) > 1"
            cursor.execute(query)
            data = cursor.fetchall()

            for item in data:
                activity_id = item[0]
                log.info(activity_id)


        except mysql.connector.Error as err:
            log.error(f"Error: {err}")
    def get_specific(self, table="", where="1=1", order_by="id", order_by_type="asc", custom=""):
        try:
            if custom != "":
                query = custom
            else:
                query = f"SELECT * FROM {table} WHERE {where} ORDER BY {order_by} {order_by_type}"

            cursor = self.cnx.cursor()  # Get cursor from existing connection
            # log.info(query)
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except Exception as e:
            return e
    def close(self):  # Method to close connection when done
        self.cnx.close()
