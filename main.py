import threading
from tkinter import *
# import ttkbootstrap as ttk
import tkinter.messagebox
from ttkbootstrap import Notebook, ScrolledText, Button, Entry, StringVar
from httpx import get
from base64 import b64encode
from ipaddress import IPv4Address
from configparser import ConfigParser

cfg = ConfigParser()


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.setDaemon(True)
        self.start()  # 在这里开始

    def run(self):
        self.func(*self.args)


class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_input_input = self.__tk_input_input()
        self.tk_button_search = self.__tk_button_search()
        self.tk_tabs = Tabs_results(self)

    def __win(self):
        self.title("inforgation信息聚合")
        # 设置窗口大小、居中
        width = 607
        height = 540
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)

    # 主界面输入框
    def __tk_input_input(self):
        ipt = Entry(self)
        ipt.place(x=170, y=5, width=300, height=30)
        return ipt

    # 主界面查询按钮
    def __tk_button_search(self):
        btn = Button(self, text="查询", command=self.__schedule)
        btn.place(x=490, y=5, width=102, height=30)
        return btn

    def __schedule(self):
        self.__save_config()

    def __save_config(self):
        if not cfg.has_section('fofa'):
            cfg.add_section('fofa')
        cfg.set('fofa', 'mail', self.tk_tabs.tk_tabs_config.tk_label_frame_fofa.tk_input_fofa_mail.get())
        cfg.set('fofa', 'apikey', self.tk_tabs.tk_tabs_config.tk_label_frame_fofa.tk_input_fofa_key.get())
        if not cfg.has_section('hunter'):
            cfg.add_section('hunter')
        cfg.set('hunter', 'username', self.tk_tabs.tk_tabs_config.tk_label_frame_hunter.tk_input_hunter_username.get())
        cfg.set('hunter', 'apikey', self.tk_tabs.tk_tabs_config.tk_label_frame_hunter.tk_input_hunter_key.get())
        if not cfg.has_section('weibu'):
            cfg.add_section('weibu')
        cfg.set('weibu', 'apikey', self.tk_tabs.tk_tabs_config.tk_label_frame_weibu.tk_input_weibu_key.get())
        if not cfg.has_section('0zero'):
            cfg.add_section('0zero')
        cfg.set('0zero', 'apikey', self.tk_tabs.tk_tabs_config.tk_label_frame_0zero.tk_input_0zero_key.get())
        if not cfg.has_section('shodan'):
            cfg.add_section('shodan')
        cfg.set('shodan', 'apikey', self.tk_tabs.tk_tabs_config.tk_label_frame_shodan.tk_input_shodan_key.get())
        if not cfg.has_section('zoomeye'):
            cfg.add_section('zoomeye')
        cfg.set('zoomeye', 'apikey', self.tk_tabs.tk_tabs_config.tk_label_frame_zoomeye.tk_input_zoomeye_key.get())
        cfg.write(open("config.ini", 'w'))


# 结果页，主要的显示区域
class Tabs_results(Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.__frame()

    def __frame(self):
        self.tk_tabs_fofa = Frame_results(self)
        self.add(self.tk_tabs_fofa, text="FOFA")

        self.tk_tabs_hunter = Frame_results(self)
        self.add(self.tk_tabs_hunter, text="鹰图")

        self.tk_tabs_weibu = Frame_results(self)
        self.add(self.tk_tabs_weibu, text="微步")

        self.tk_tabs_0zero = Frame_results(self)
        self.add(self.tk_tabs_0zero, text="0zero")

        self.tk_tabs_shodan = Frame_results(self)
        self.add(self.tk_tabs_shodan, text="shodan")

        self.tk_tabs_zoomeye = Frame_results(self)
        self.add(self.tk_tabs_zoomeye, text="zoomeye")

        self.tk_tabs_config = Frame_config(self)
        self.add(self.tk_tabs_config, text="config")

        self.place(x=10, y=40, width=585, height=480)


# 结果页的frame
class Frame_results(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.__frame()
        self.tk_text = self.__tk_text()

    def __frame(self):
        self.place(x=10, y=40, width=585, height=480)

    def __tk_text(self):
        text = ScrolledText(self)
        text.place(x=10, y=10, width=565, height=430)
        return text


# 配置页的总frame
class Frame_config(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.__frame()
        self.__check_config()
        self.tk_label_frame_fofa = Frame_config_fofa(self, self.fofa_mail, self.fofa_key)
        self.tk_label_frame_hunter = Frame_config_hunter(self, self.hunter_username, self.hunter_key)
        self.tk_label_frame_weibu = Frame_config_weibu(self, self.weibu_key)
        self.tk_label_frame_0zero = Frame_config_0zero(self, self._0zero_key)
        self.tk_label_frame_shodan = Frame_config_shodan(self, self.shodan_key)
        self.tk_label_frame_zoomeye = Frame_config_zoomeye(self, self.zoomeye_key)

    def __frame(self):
        self.configure()
        self.place(x=10, y=40, width=585, height=480)

    def __check_config(self):
        read_ok = cfg.read('config.ini', encoding='utf-8')
        if not read_ok:
            tkinter.messagebox.showinfo(title="info",
                                        message=f"未在当前目录检测到config.ini，请在config页进行配置，进行查询后回将配置保存到当前目录的config.ini")
            self.fofa_mail = StringVar(value="")
            self.fofa_key = StringVar(value="")
            self.hunter_username = StringVar(value="")
            self.hunter_key = StringVar(value="")
            self.weibu_key = StringVar(value="")
            self._0zero_key = StringVar(value="")
            self.shodan_key = StringVar(value="")
            self.zoomeye_key = StringVar(value="")
        else:
            # fofa配置
            # mail
            try:
                self.fofa_mail = StringVar(value=cfg['fofa']['mail'])
            except KeyError:
                self.fofa_mail = StringVar(value="")
            # apikey
            try:
                self.fofa_key = StringVar(value=cfg['fofa']['apikey'])
            except KeyError:
                self.fofa_key = StringVar(value="")
            # hunter配置
            # username
            try:
                self.hunter_username = StringVar(value=cfg['hunter']['username'])
            except KeyError:
                self.hunter_username = StringVar(value="")
            # apikey
            try:
                self.hunter_key = StringVar(value=cfg['hunter']['apikey'])
            except KeyError:
                self.hunter_key = StringVar(value="")
            # 微步配置
            try:
                self.weibu_key = StringVar(value=cfg['weibu']['apikey'])
            except KeyError:
                self.weibu_key = StringVar(value="")
            # 0zero
            try:
                self._0zero_key = StringVar(value=cfg['0zero']['apikey'])
            except KeyError:
                self._0zero_key = StringVar(value="")
            # shodan
            try:
                self.shodan_key = StringVar(value=cfg['shodan']['apikey'])
            except KeyError:
                self.shodan_key = StringVar(value="")
            # zoomeye
            try:
                self.zoomeye_key = StringVar(value=cfg['zoomeye']['apikey'])
            except KeyError:
                self.zoomeye_key = StringVar(value="")


# 配置页的fofa frame
class Frame_config_fofa(LabelFrame):
    def __init__(self, parent, fofa_mail, fofa_key):
        super().__init__(parent)
        self.fofa_key = fofa_key
        self.fofa_mail = fofa_mail
        self.__frame()
        self.tk_input_fofa_mail = self.__tk_input_fofa_mail()
        self.tk_input_fofa_key = self.__tk_input_fofa_key()
        self.tk_label_fofa_mail = self.__tk_label_fofa_mail()
        self.tk_label_fofa_key = self.__tk_label_fofa_key()

    def __frame(self):
        self.configure(text="fofa", background="")
        self.place(x=10, y=20, width=565, height=80)

    def __tk_input_fofa_mail(self):
        ipt = Entry(self, textvariable=self.fofa_mail)
        ipt.place(x=80, y=0, width=475, height=24)
        return ipt

    def __tk_input_fofa_key(self):
        ipt = Entry(self, textvariable=self.fofa_key)
        ipt.place(x=80, y=30, width=475, height=24)
        return ipt

    def __tk_label_fofa_mail(self):
        label = Label(self, text="邮箱")
        label.place(x=10, y=0, width=68, height=24)
        return label

    def __tk_label_fofa_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=30, width=68, height=24)
        return label


# 配置页的鹰图frame
class Frame_config_hunter(LabelFrame):
    def __init__(self, parent, hunter_username, hunter_key):
        super().__init__(parent)
        self.hunter_key = hunter_key
        self.hunter_username = hunter_username
        self.__frame()
        self.tk_input_hunter_username = self.__tk_input_hunter_username()
        self.tk_input_hunter_key = self.__tk_input_hunter_key()
        self.tk_label_hunter_username = self.__tk_label_hunter_username()
        self.tk_label_hunter_key = self.__tk_label_hunter_key()

    def __frame(self):
        self.configure(text="鹰图", background="")
        self.place(x=10, y=110, width=565, height=80)

    def __tk_input_hunter_username(self):
        ipt = Entry(self, textvariable=self.hunter_username)
        ipt.place(x=80, y=0, width=475, height=24)
        return ipt

    def __tk_input_hunter_key(self):
        ipt = Entry(self, textvariable=self.hunter_key)
        ipt.place(x=80, y=30, width=475, height=24)
        return ipt

    def __tk_label_hunter_username(self):
        label = Label(self, text="用户名")
        label.place(x=8, y=0, width=68, height=24)
        return label

    def __tk_label_hunter_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=8, y=30, width=68, height=24)
        return label


# 配置页的微步frame
class Frame_config_weibu(LabelFrame):
    def __init__(self, parent, weibu_key):
        super().__init__(parent)
        self.weibu_key = weibu_key
        self.__frame()
        self.tk_input_weibu_key = self.__tk_input_weibu_key()
        self.tk_label_weibu_key = self.__tk_label_weibu_key()

    def __frame(self):
        self.configure(text="微步", background="")
        self.place(x=10, y=200, width=565, height=51)

    def __tk_input_weibu_key(self):
        ipt = Entry(self, textvariable=self.weibu_key)
        ipt.place(x=80, y=0, width=475, height=24)
        return ipt

    def __tk_label_weibu_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=8, y=0, width=68, height=24)
        return label


# 配置页的0zero frame
class Frame_config_0zero(LabelFrame):
    def __init__(self, parent, zero_key):
        super().__init__(parent)
        self.zero_key = zero_key
        self.__frame()
        self.tk_input_0zero_key = self.__tk_input_0zero_key()
        self.tk_label_0zero_key = self.__tk_label_0zero_key()

    def __frame(self):
        self.configure(text="0zero", background="")
        self.place(x=10, y=260, width=565, height=51)

    def __tk_input_0zero_key(self):
        ipt = Entry(self, textvariable=self.zero_key)
        ipt.place(x=80, y=0, width=475, height=24)
        return ipt

    def __tk_label_0zero_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=0, width=68, height=24)
        return label


# 配置页的shodan frame
class Frame_config_shodan(LabelFrame):
    def __init__(self, parent, shodan_key):
        super().__init__(parent)
        self.shodan_key = shodan_key
        self.__frame()
        self.tk_input_shodan_key = self.__tk_input_shodan_key()
        self.tk_label_shodan_key = self.__tk_label_shodan_key()

    def __frame(self):
        self.configure(text="shodan", background="")
        self.place(x=10, y=320, width=565, height=51)

    def __tk_input_shodan_key(self):
        ipt = Entry(self, textvariable=self.shodan_key)
        ipt.place(x=80, y=0, width=475, height=24)
        return ipt

    def __tk_label_shodan_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=0, width=68, height=24)
        return label


# 配置页的zoomeye frame
class Frame_config_zoomeye(LabelFrame):
    def __init__(self, parent, zoomeye_key):
        super().__init__(parent)
        self.zoomeye_key = zoomeye_key
        self.__frame()
        self.tk_input_zoomeye_key = self.__tk_input_zoomeye_key()
        self.tk_label_zoomeye_key = self.__tk_label_zoomeye_key()

    def __frame(self):
        self.configure(text="zoomeye", background="")
        self.place(x=10, y=380, width=565, height=51)

    def __tk_input_zoomeye_key(self):
        ipt = Entry(self, textvariable=self.zoomeye_key)
        ipt.place(x=80, y=0, width=475, height=24)
        return ipt

    def __tk_label_zoomeye_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=0, width=68, height=24)
        return label


class Win(WinGUI):
    def __init__(self):
        super().__init__()
        self.__event_bind()

    def __event_bind(self):
        pass


if __name__ == "__main__":
    root = Win()
    root.mainloop()
