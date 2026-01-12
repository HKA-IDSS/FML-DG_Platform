import os
from pathlib import Path
from typing import Optional
import pymysql
import pymysql.cursors
import yaml
import pandas as pd


class MySQL:
    def __init__(self, path=None, timeout_ms: Optional[int] = None):
        if path:
            config_path = path
        else:
            config_path = Path(os.path.dirname(__file__)) / 'config.yml'

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        url = config["mysqlconfig"]["dburl"]
        port = config["mysqlconfig"]["port"]
        username = config["mysqlconfig"]["user"]
        password = config["mysqlconfig"]["password"]
        database = config["mysqlconfig"]["database"]


        results_url = "mysql+pymysql://" + url + ":" + password + "@" + username + port + "/" + database
        conn = pymysql.connect(host=url,
                               user=username,
                               password=password,
                               cursorclass=pymysql.cursors.DictCursor)
        conn.cursor().execute("create database if not exists " + database)

        self.conn = conn

    def insert_new_results(self, training_id, metric, dataframe: pd.DataFrame):
        columns = dataframe.columns
        sql = "CREATE TABLE " + training_id + "_" + metric + "("

        sql += columns[0] + " float"
        for column in columns[1:]:
            sql += ", " + column + " float"
        sql += ");"

        with self.conn.cursor() as cursor:
            cursor.execute(sql)
        self.conn.commit()

        with self.conn.cursor() as cursor:
            for index, row in dataframe.iterrows():
                sql = "INSERT INTO " + training_id + "_" + metric + " VALUES "
                sql += (index) + tuple(row.values)
                sql += ";"
                cursor.execute(sql)
            self.conn.commit()



