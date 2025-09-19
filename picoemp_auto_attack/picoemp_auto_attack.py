import serial
import time
import random
from cushy_serial import CushySerial
import enum 
class Status(enum.Enum):
    shutdown = 0
    ins_fault=1
    IO_fault=2
    reset=3
    normal=4


class PicoEMP:
    def __init__(self, port, baudrate=115200, timeout=0.4):
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        #self.ser = CushySerial(port.upper(), baudrate)
        if not self.ser.is_open:
            raise Exception('Serial port not open')
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self._send(b'h\r\n')

    def _send(self, command):
        self.ser.write(command)
        self.ser.flush()

    def _read(self):
        byte_data=self.ser.read_all()
        # if DEBUG:
        #     print(byte_data.decode(),end='')
        return byte_data

    def _close(self):
        self.ser.close()
        
    def arm(self):
        self._send('a\r\n'.encode('ascii'))

        return self._read().decode()
    
    
    def disarm(self):
        self._send(b'd\r\n')
        return self._read().decode()
    
    
    def manual_pulse(self):
        self._send(b'p\r\n')
        return self._read().decode()
    
    
    def status(self):
        self._send(b's\r\n')
        return self._read().decode()
    
    def reset(self):
        self._send(b'r\r\n')
        return self._read().decode()
    
    def configure(self,
                  pulse_time:int,
                  pulse_power:float,
                  delay_cycles:int,
                  time_cycles:int):
        
        self._send(b'c\r\n')
        self._send(f'{pulse_time} {pulse_power} {delay_cycles} {time_cycles}\r\n'.encode())
        return self._read().decode()

    def trigger(self):
        self._send(b'f\r\n')  
    
    def reset_target(self):
        self._send(b't\r\n')
        time.sleep(0.1)
        self._send(b't\r\n')
        return self._read().decode()
    
    def close(self):
        self._close()

class StatusString:
    SUCCESS="("
    RESET="RESET"
    
    
    
    
class Target:
    def __init__(self, port, baudrate=115200, timeout=0.4):
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        #self.ser = CushySerial(port.upper(), baudrate)
        if not self.ser.is_open:
            raise Exception('Serial port not open')
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def _send(self, command):
        self.ser.write(command)
        self.ser.flush()

    def _read(self):
        bytes_data=self.ser.read_all()
        return bytes_data

    def _close(self):
        self.ser.close()
        
    def check_target_status(self,timeout:float=0.5):
        # todo: 修改此处以适配不同目标程序返回的结果类型
        start_time = time.time()
        no_response_flag=True
        while time.time()-start_time < timeout:
            res=self._read()
            if len(res) != 0:
                no_response_flag=False
            else:
                continue
            recv_ascii=""
            non_ascii_count=0
            for i in res:
                if 0< i <128:
                    recv_ascii+=chr(i)
                else:
                    non_ascii_count+=1
            # print(res)
            print(recv_ascii,end="")
            if non_ascii_count/len(res)>=0.5:
                return Status.IO_fault
            
            # 存在特定字符串，表示故障成功
            if StatusString.SUCCESS in recv_ascii:
                return Status.ins_fault
            
            # 存在复位对应的特定字符串 "RESET"
            if StatusString.RESET in recv_ascii:
                return Status.reset
            
        # timeout
        if no_response_flag:
            # 超时无响应，判断为停机
            return Status.shutdown
        else:
            # 存在响应，判断为正常
            return Status.normal
    def close(self):
        self._close()
        
statics={
        Status.IO_fault:0,
        Status.ins_fault:0,
        Status.reset:0,
        Status.shutdown:0,
        Status.normal:0
    }        

DEBUG=False
def attack(emp_port:str,target_port:str):
    picoemp = PicoEMP(emp_port)
    target = Target(target_port)
    
    pulse_time=5
    pulse_power=0.0122
    delay_cycles=300
    time_cycles=625
    
    try:
        # picoemp.reset()
        time.sleep(1)
        picoemp.arm() # charge
        while True:
            # gen parameters
            #pulse_time=4
            # pulse_power=random.uniform(0.01,0.02)
            # delay_cycles=random.randint(600,720)
            #delay_cycles=random.randint(300,310)
            # time_cycles=624
            picoemp.configure(
                pulse_time,
                pulse_power,
                delay_cycles,
                time_cycles
            )
            print(f"pulse time:{pulse_time:4} pulse power：{pulse_power:4f} delay:{delay_cycles:4} time cycles:{time_cycles:4}",end="   ")
            # trigger once
            picoemp.trigger()
            time.sleep(0.2)
            
            # check target status
            status=target.check_target_status(1)
            statics[status]+=1
            if status == Status.shutdown:
                print("shutdown fault")
                picoemp.reset_target()
                picoemp.reset_target()
            elif status == Status.ins_fault:
                print(" ins fault")
            elif status == Status.IO_fault:
                print(" IO fault")
                picoemp.reset_target()
            elif status == Status.reset:
                print(" reset fault")
            elif status == Status.normal:
                print(" normal")
            else:
                print(" unknown")

    except Exception as e:
        print(f"Exception:{e}")
        import traceback
        traceback.print_exc()
        picoemp.disarm()
        picoemp.reset()
        picoemp.close()
        target.close()
        
    except KeyboardInterrupt:
        print("keyboard interrupt")
        picoemp.disarm()
        picoemp.reset()
        picoemp.close()
        target.close()
        print(statics)
        
'''
680-700-720
'''
if __name__ == '__main__':
    attack('com51','com53')