import pyodbc
import time
import functools
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
                cls._instances[line_id].base_for_write = cls._instances[line_id].line.base
                cls._instances[line_id].table = cls._instances[line_id].base_for_write.nameBaseTable
                cls._instances[line_id].connection = None
            return cls._instances[line_id]
        
    
    def init_line_for_db(func):
        @functools.wraps(func)
        def wrapper_decorator(self, value_name, start_time, end_time):
            if int(self.line_id) != 4:
                result = self.get_data_type_2(value_name, start_time, end_time)
            else:
                result = func(self, value_name, start_time, end_time)
            return result
        return wrapper_decorator
        

    def connect(self):
        try:
            base_for_write = self.base_for_write
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
            return True
        except Exception as e:
            print("ОШбочка при записи:",e)
            self.disconnect
            return False

    @init_line_for_db
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
        
    
    def get_data_type_2(self, value_name, start_time, end_time):
        """Временная функция, которая используется через декоратор к основной get_data
           в случае использование таблицы с другой структурой, т.к. к программе ПЛК доступа пока что нет,
           и данные мы получаем с другого датчика"""

        if value_name:
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
                    CAST(Name AS varchar(max)) = ? AND TimeStamp >= ? AND Timestamp <= ?
            """, value_name, start_time, end_time)
            print(f"Данные на промежутке от {start_time} to {end_time} Получены для {value_name}")

            result = cursor.fetchall()
            return result
        else:
            print(f"Данные для влажности отсутствуют")
            return []
        
        
    def delete_old_data(self, days=180):
        try:
            if not self.connection:
                print(f"Нет подключения к бд: {self.connection}")
                self.connect()
            date = datetime.now() - timedelta(days)
            cursor = self.connection.cursor()

            cursor.execute(f"""
                delete FROM {self.table}
                WHERE
                    TimeStamp < ?
            """, date)

            self.connection.commit()
            print(f"Удалены данные до {date}")
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
