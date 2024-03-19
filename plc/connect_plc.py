import snap7
import time
import struct

from laboratory.models import *


class PLC_Semiens:
    def __init__(self, plc: PLC) -> None:
        self.plc = plc
        self.line = self.plc.line_id
        self.chamber = self.plc.chamber
        self.client = snap7.client.Client()
        self.time_update = self.line.TimeSecUpdate
        self.status = ""

    def connect(self):
        try:
            self.client.connect(self.plc.adress, 0, 1, 102)
            self.status = "connected"
            return True
        except RuntimeError:
            return False
    

    def get_data(self) -> dict[str:float]:
        try:
            if not self.client.get_connected():
                self.client.connect(self.plc.adress, 0, 1, 102)

            data_bytes = self.client.db_read(150, 0, 8)
            air_temp, humidity = struct.unpack('>ff', data_bytes)
            result = {f'{self.plc.PLCName}_{self.plc.chamber}_air_temp': round(float(air_temp),2), 
                    f'{self.plc.PLCName}_{self.plc.chamber}_humidity': round(float(humidity),2)}
            return result
        except Exception as e:
            print(f"При получении данных ошибка: {e}")
            return {}
        

    def disconnect(self):
        try:
            self.client.disconnect()
        except Exception as e:
            print("Ошибка при отключении от ПЛК: ", e)
