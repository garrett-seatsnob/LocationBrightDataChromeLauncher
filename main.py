import tkinter
import tkinter.ttk as ttk
import sys
import subprocess
import os
import requests
import pathlib
import logging

logger = logging.getLogger(__name__)
exception_logger = logging.getLogger(__name__ + '_exc_tb')

# Command line args will be platform dependent. Chrome cmd opens chrome configured to the given proxy/port
if sys.platform == 'win32':
    chrome_cmd = r'start chrome https://ipstack.com/ --user-data-dir="%UserProfile%\.temp-evenue-chrome_{port}" ' \
                 r'--load-extension={extension_dir} ' \
                 r'--proxy-server=http://{proxy_ip}:{port} --no-first-run'
elif sys.platform == 'linux':
    chrome_cmd = r'google-chrome https://ipstack.com/ --user-data-dir=~\.temp-evenue-chrome_{port} ' \
                 r'--load-extension={extension_dir} ' \
                 r'--proxy-server=http://{proxy_ip}:{port} --no-first-run'
elif sys.platform == 'darwin':
    chrome_cmd = r'open -a "Google Chrome" https://ipstack.com/ ' \
                 r'--user-data-dir=~\.temp-evenue-chrome_{port}" ' \
                 r'--load-extension={extension_dir} ' \
                 r'--proxy-server=http://{proxy_ip}:{port} --no-first-run'
else:
    raise ValueError(
        f"I'm not sure what platform I am running on; expecting one of [win32, linux, darwin], got {sys.platform}")


class LogWidget(tkinter.Text):
    def write(self, s: str):
        self.configure(state='normal')
        self.insert(tkinter.END, s)
        self.configure(state='disabled')


def select_on_focus(event):
    """
    Trigger function on select that highlights the text in the entry field
    :param event:
    :return:
    """
    event.widget.select_range(0, tkinter.END)


ext_dir = pathlib.Path()


def launch_chrome():
    """
    Launches chrome by executing cmd line argument(s) from chrome_cmd while interpolating apporpriate values from
    the tkinter variables
    :return:
    """
    port_value = port.get()
    proxy_value = proxy.get()
    extension_dir = pathlib.Path(os.getcwd()) / ext_dir
    logger.info(f'Launching port {port_value}')
    subprocess.run(chrome_cmd.format(port=port_value, extension_dir=extension_dir, proxy_ip=proxy_value), shell=True)


proxy_dummy_port = None
proxy_dummy_addr = None


def get_ports():
    """
    Get a currently active list of ports from the brightdata api. Set the width and choices of the port dropdown based
    on the retrieved list.
    :return:
    """
    try:
        r = requests.get(f'http://{proxy_dummy_addr}:{proxy_dummy_port}/api/proxies_running')
    except requests.ConnectionError:
        logger.error(
            'Failed to connect to the proxy middleman to retrieve the proxy list. If the problem consists, please '
            'contact your system admin.'
        )
        return
    except Exception:
        exception_logger.exception('Unhandled exception getting proxies')
        logger.error('Unhandled exception getting proxies')
        return
    if r.status_code != 200:
        logger.error(f'Failed to retrieve running proxies: {r.status_code} {r.text}')
        return
    j = r.json()
    proxies = list()
    max_list_val_width = None
    for proxy_dict in j:
        if proxy_dict['zone'] == 'purchasing_res_target_area':
            try:
                raw_state = proxy_dict['state']
            except KeyError:
                state = 'Any State'
            else:
                state = raw_state.upper()

            try:
                city = proxy_dict['city']
            except KeyError:
                city = 'Any City'
            list_val = f"{state} -- {city}: {proxy_dict['port']}"
            if max_list_val_width is None:
                port_combo_var.set(list_val)
                update_port()
                max_list_val_width = len(list_val)
            else:
                max_list_val_width = max(max_list_val_width, len(list_val))
            proxies.append(list_val)
    port_combo.configure(values=proxies, width=max_list_val_width + 2)


def update_port(_=None):
    port_combo_option = port_combo_var.get()
    try:
        _, port_val = port_combo_option.split(': ')
    except ValueError:
        logger.debug(f'Could not find port in {port_combo_option}')
        return

    port.set(int(port_val))


root = tkinter.Tk()
root.title("Evenue Chrome Window Launcher")

mainframe = ttk.Frame(root, padding="30 30 30 30")
mainframe.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

ttk.Label(mainframe, text="port").grid(column=0, row=0)
port = tkinter.IntVar()
port_combo_var = tkinter.StringVar()
port_combo = ttk.Combobox(mainframe, width=15, values=list(), state=['readonly'], textvariable=port_combo_var)
port_combo.grid(column=1, row=0, sticky=(tkinter.W, tkinter.E))
port_combo.bind("<<ComboboxSelected>>", update_port)
ttk.Button(mainframe, text="Refresh ports", command=get_ports).grid(column=2, row=0, sticky=(tkinter.W, tkinter.E))

ttk.Label(mainframe, text="proxy").grid(column=0, row=1)
proxy = tkinter.StringVar()
proxy_entry = ttk.Entry(mainframe, width=15, textvariable=proxy)
proxy_entry.grid(column=1, row=1, sticky=(tkinter.W, tkinter.E))
proxy_entry.bind("<FocusIn>", select_on_focus)

ttk.Button(mainframe, text="Launch", command=launch_chrome).grid(column=2, row=1, sticky=(tkinter.W, tkinter.E))

log_box = LogWidget(mainframe, state='disabled', wrap=tkinter.WORD)
log_box.grid(column=0, row=2, sticky=(tkinter.W, tkinter.E), columnspan=3)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.bind("<Return>", launch_chrome)


if __name__ == '__main__':
    import argparse
    import sys
    import configparser

    parser = argparse.ArgumentParser()
    parser.add_argument('cfg_dir', type=pathlib.Path)
    parser.add_argument('ext_dir', type=pathlib.Path)
    parser.add_argument('--verbosity', '-v', type=int, default=20)
    parser.add_argument('--proxy_mgr_addr', default='23.122.184.253')
    parser.add_argument('--proxy_dummy_addr', default='99.29.228.57')
    parser.add_argument('--proxy_dummy_port', type=int, default=23000)
    args_ = parser.parse_args()

    cfg_parser = configparser.ConfigParser()
    bots_cfg_path = args_.cfg_dir / 'EvenueChromeLauncher.cfg'
    with open(bots_cfg_path) as f:
        cfg_parser.read_file(f)

    tkinter_formatter = logging.Formatter(cfg_parser['main']['gui_log_fmt'])
    tkinter_handler = logging.StreamHandler(log_box)
    tkinter_handler.setLevel(args_.verbosity)
    tkinter_handler.setFormatter(tkinter_formatter)
    logger.setLevel(args_.verbosity)
    logger.addHandler(tkinter_handler)

    exception_log_formatter = logging.Formatter(cfg_parser['main']['console_log_fmt'])
    exception_log_handler = logging.StreamHandler(sys.stderr)
    exception_log_handler.setLevel(logging.ERROR)
    exception_logger.setLevel(logging.ERROR)
    exception_logger.addHandler(exception_log_handler)

    ext_dir = args_.ext_dir
    proxy_dummy_addr = args_.proxy_dummy_addr
    proxy_dummy_port = args_.proxy_dummy_port
    proxy.set(args_.proxy_mgr_addr)

    root.mainloop()
