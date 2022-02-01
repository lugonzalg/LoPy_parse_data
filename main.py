import  pycom;
import  socket;
import  time;
import  ubinascii;
from    machine import UART;
from    network import LoRa;

pycom.heartbeat(False);
BAUD_RATE = 19200
send_tab = [""] * 20;
app_eui = ubinascii.unhexlify('0000000000000000');
app_key = ubinascii.unhexlify('11B0282A189B75B0B4D2D8C7FA38548B');

def ft_UART_serial_com(uart):
    recv = uart.read();
    if (recv):
        ft_trim_data(recv)
    else:
        print("Nothing to read.");

def ft_trim_data(recv):
    i = 0;
    j = 0;
    raw_tab = str(recv)
    tab = raw_tab.split('\\r\\n')
    tab_len = len(tab)
    while (i < 20):
        tab_split = tab[i + j].split('\\t')
        if (len(tab_split) < 2 or (i == 0 and tab_split[0] != "PID")):
            j += 1;
            continue ;
        send_tab[i] = tab_split[1];
        i += 1
        if (tab_split[0] == 'HSDS'):
            break ;

def ft_init_UART_com():
    uart = UART(1, BAUD_RATE, bits=8, parity=None, stop=1)
    uart.init(baudrate= BAUD_RATE, bits=8, parity=None, stop=1, timeout_chars=2, pins=("P3", "P4"))
    return uart;

def ft_init_LORA():
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    #CONECTARSE A LORA
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
    while (not lora.has_joined()):
        pycom.rgbled(0x140000) #RED
        time.sleep(2.5)
        pycom.rgbled(0x000000) #NO_COLOR
        time.sleep(1.0)
        print('Estableciendo conexión LoRa.');
    pycom.rgbled(0x001400) #RED
    print('Conexión LoRa establecido.')
    return (lora);

def ft_init_socket():
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    return (s)

def ft_send_list(s):
    i = 0;
    size_send_tab = len(send_tab);
    send_str = "";
    #to_Volt = float(int(send_tab[3]) / 1000);
    send_str += str(float(int(send_tab[3]) / 1000)) + " ,";
    send_str += str(float(int(send_tab[4]) / 1000)) + " ,";
    send_str += send_tab[10];
    #send_str = ubinascii.b2a_base64(send_str);
    send_str = bytes(send_str, 'UTF-8')
    s.send(send_str);

def main():
    lora = ft_init_LORA();
    #print(ubinascii.hexlify(lora.mac()).decode('utf-8'))
    s = ft_init_socket();
    uart = ft_init_UART_com();
    while True:
        ft_UART_serial_com(uart);
        if (len(send_tab[0]) == 0):
            time.sleep(10);
            continue ;
        ft_send_list(s);
        print('[' + str(time.time()) + ']' + 'TIMESTAMP');
        time.sleep(10);

main()
