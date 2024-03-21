import pyodbc
import time
import numpy as np
from datetime import datetime, timedelta
import threading
from .models import CurtecSensors, BaseForWrite, Line  # Замените на имя вашего приложения


class DatabaseLineManager:
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, line_id):
        with cls._lock:
            if line_id not in cls._instances:
                cls._instances[line_id] = super(DatabaseLineManager, cls).__new__(cls)
                cls._instances[line_id].line_id = line_id
                cls._instances[line_id].line = Line.objects.get(id=line_id)
                cls._instances[line_id].table = cls._instances[line_id].line.nameBaseTable
                cls._instances[line_id].connection = None
            return cls._instances[line_id]
        

    def __init__(self, line_id):
        self.line_id = line_id
        self.line = Line.objects.get(id=line_id)
        self.table = self.line.nameBaseTable

    def connect(self):
        try:
            base_for_write = BaseForWrite.objects.get(id=1)
            connection_string = f"DRIVER={{SQL Server}};SERVER={base_for_write.server};DATABASE={base_for_write.base};UID={base_for_write.user};PWD={base_for_write.password};"
            self.connection = pyodbc.connect(connection_string)
            print("Подключение к базе данных установлено")
            return True
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            return False

    def disconnect(self):
        try:
            if self.connection:
                self.connection.close()
                print("Disconnected from the database")
        except Exception as e:
            print(f"Error disconnecting from the database: {e}")
        finally:
            self.connection = None

    def insert_data(self, value_name, value):
        try:
            if not self.connection:
                print("Нет подключения к базе данных!")
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute(f"INSERT INTO {self.table} (TimeStamp, ValueName, Value) VALUES (GETDATE(), ?, ?)",
                        value_name, value)

            self.connection.commit()
            print("ВНИМАНИЕ! ЗАПИСИ В БД НЕТ. ТЕСТ!!!!")
            return True
        except Exception as e:
            print("ОШбочка при записи:",e)
            self.disconnect
            return False


    def get_data(self, value_name, start_time, end_time):
        """ Для получения данных инициализируется отдельный объект класса и новое подключение"""

        try:
            if not self.connection:
                print(f"Нет подключения к бд: {self.connection}")
                self.connect()

            cursor = self.connection.cursor()

            cursor.execute(f"""
                SELECT
                    Value,
                    Timestamp,
                    ROW_NUMBER() OVER (ORDER BY Timestamp) as RowNum
                FROM
                    {self.table}
                WHERE
                    ValueName = ? AND TimeStamp >= ? AND Timestamp <= ?

            """, value_name, start_time, end_time)
            print(f"Данные на промежутке от {start_time} to {end_time} Получены")


            result = cursor.fetchall()
            return result

        except pyodbc.Error as e:
            print(f"Error retrieving data: {e}. При запросе {value_name}")
            return []
        except Exception as e:
            print(f"Ошибка при подключении к бд: {e}")
            return []
        
    def delete_old_data(self, days):
        try:
            if not self.connection:
                print(f"Нет подключения к бд: {self.connection}")
                self.connect()
            date = datetime.now() - timedelta(days=180)
            cursor = self.connection.cursor()

            cursor.execute(f"""
                delete FROM {self.table}
                WHERE
                    TimeStamp < ?
            """, date)

            self.connection.commit()
            print(f"Удалены данные, записанные ранее, чем {date}")
            return True
        except Exception as e:
            print("Ошибка при удалении данных:", e)
            return False


def interpolation_data(data, interpolation_points):
    if len(data) < interpolation_points:
        return data
    
    values, timestamps, _ = zip(*data)

    timestamps_sec = [(t - timestamps[0]).total_seconds() for t in timestamps]

    
    new_timestamps_sec = np.linspace(timestamps_sec[0], timestamps_sec[-1], interpolation_points)
    new_timestamps = [timestamps[0] + timedelta(seconds=t) for t in new_timestamps_sec]

    new_values = np.interp(new_timestamps_sec, timestamps_sec, values)

    new_data = list(zip(new_values, new_timestamps, range(1, interpolation_points + 1)))
    return new_data
