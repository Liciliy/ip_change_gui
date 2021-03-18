from API_core.api_talker import ApiRequest
import sys
import time

from threading import Thread

import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import main

import netifaces

from ip_operations import NetworkHandler


# === Layout definition ===================================================== #
CHANGE_IP_BTN = 'Change IP'
TEXT_KEY      = '-GreetText-'
BTN_KEY       = '-ChangeIpBtn-'

text_object = sg.Text("Push below button to change external IP", key = TEXT_KEY)
change_ip_btn = sg.Button(CHANGE_IP_BTN, key = BTN_KEY)

horizontal_sep = sg.HorizontalSeparator(color = 'green')

exec_log_text = sg.Text("Execution log:")

output_window = sg.Output(echo_stdout_stderr = True, size=(90,20))

layout = [[text_object], [change_ip_btn], 
          [horizontal_sep], 
          [exec_log_text], [output_window]]
# =========================================================================== #


class State:
    ip_change_in_progress = None
    closing = None

    def __init__(self) -> None:
        self.ip_change_in_progress = False 
        self.closing = False


def change_ip(program_state : State):

    try:
        conn_details = NetworkHandler.get_connection_details()


        api_request = ApiRequest(conn_details[NetworkHandler.DEFAULT_GATEWAY])

        new_gate = api_request.get_new_gate()

        if NetworkHandler.change_default_gateway(new_gate):
            api_request.confirm_gate_usage_towards_api(new_gate)
            print('Success')
        else:
            # TODO Here send failed result to the gateway
            print('Failed')

    except Exception as ex:
        err_text = \
          f'AN ERROR OCCURRED! Error text: {str(ex)}. Please contact support.\n'

        print(err_text)

    finally:
        if not state.closing: 
            program_state.ip_change_in_progress = False
            window.FindElement(BTN_KEY).Update(disabled=False)


if __name__ == '__main__':

    sys_encoding = sys.stdout.encoding

    NetworkHandler.set_encoding(sys_encoding)
    # Create the window
    window = sg.Window("IP Manager", layout, margins=(100, 25))

    state = State()
    ip_change_thread : Thread = None

    # Create an event loop
    while True:
        event, values = window.read()
        
        if event == BTN_KEY and not state.ip_change_in_progress:

            state.ip_change_in_progress = True    
            window.FindElement(BTN_KEY).Update(disabled=True)

            ip_change_thread = Thread(target = change_ip, 
                                      args = (state, ))

            ip_change_thread.start()
    
        if event == sg.WIN_CLOSED:
            state.closing = True
            break

    if ip_change_thread.is_alive():
        ip_change_thread.join()