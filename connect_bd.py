import psycopg2


class DatabaseConnection:
    def __enter__(self):
        self.connection = psycopg2.connect(user="postgres",
                                           password="220508qQ",
                                           host="45.80.69.152",
                                           port="5432",
                                           database="ShopDB")
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()
