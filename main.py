import threading
from tkinter import *
import tkinter.messagebox
from ttkbootstrap import Notebook, Button, Entry, StringVar, Treeview
from httpx import get, post, ReadTimeout
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
        self.tk_input_ip = self.__tk_input_ip()
        self.tk_button_search = self.__tk_button_search()
        self.tk_tabs = Tabs_results(self)

    def __win(self):
        self.title("inforgation信息聚合")
        # 设置窗口大小、居中
        width = 1000
        height = 550
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)

    # 主界面输入框
    def __tk_input_ip(self):
        ipt = Entry(self)
        ipt.place(x=670, y=5, width=200, height=30)
        return ipt

    # 主界面查询按钮
    def __tk_button_search(self):
        btn = Button(self, text="查询", command=self.__schedule)
        btn.place(x=880, y=5, width=102, height=30)
        return btn

    def __schedule(self):
        # 每次进行查询都保存一次config
        self.__save_config()
        self.target = self.tk_input_ip.get()
        if self.target == "":
            tkinter.messagebox.showerror(title="error", message="请输入目标!")
            return
        # IP格式检查
        try:
            IPv4Address(self.target)
        except:
            tkinter.messagebox.showerror(title="error", message="IP输入有误！")
            return
        # 为了避免假死，额外启用一个线程执行
        # fofa查询
        if self.tk_tabs.tk_tabs_config.fofa_key.get() != "" and self.tk_tabs.tk_tabs_config.fofa_mail.get() != "":
            MyThread(self.__get_fofa)
        else:
            self.tk_tabs.tk_tabs_fofa.tk_label['text'] = "fofa配置缺失，本次不予查询！"
        # hunter查询
        if self.tk_tabs.tk_tabs_config.hunter_username.get() != "" and self.tk_tabs.tk_tabs_config.hunter_key.get() != "":
            MyThread(self.__get_hunter)
        else:
            self.tk_tabs.tk_tabs_hunter.tk_label['text'] = "鹰图配置缺失，本次不予查询！"
        # 微步查询
        if self.tk_tabs.tk_tabs_config.weibu_key.get() != "":
            MyThread(self.__get_weibu)
        else:
            self.tk_tabs.tk_tabs_weibu.tk_label['text'] = "微步配置缺失，本次不予查询！"
        # 0zone查询
        if self.tk_tabs.tk_tabs_config.zone_key.get() != "":
            MyThread(self.__get_0zone)
        else:
            self.tk_tabs.tk_tabs_0zone.tk_label['text'] = "0zone配置缺失，本次不予查询！"
        # shodan
        if self.tk_tabs.tk_tabs_config.shodan_key.get() != "":
            MyThread(self.__get_shodan)
        else:
            self.tk_tabs.tk_tabs_shodan.tk_label['text'] = "shodan配置缺失，本次不予查询！"
        # zoomeye
        if self.tk_tabs.tk_tabs_config.zoomeye_key.get() != "":
            MyThread(self.__get_zoomeye)
        else:
            self.tk_tabs.tk_tabs_zoomeye.tk_label['text'] = "zoomeye配置缺失，本次不予查询！"

    def __get_fofa(self):
        fofa_url = f"https://fofa.info/api/v1/search/all?email={self.tk_tabs.tk_tabs_config.fofa_mail.get()}&key={self.tk_tabs.tk_tabs_config.fofa_key.get()}&qbase64={b64encode(self.target.encode()).decode()}&fields=host,title,country_name,province,city,server,protocol,isp"
        try:
            [self.tk_tabs.tk_tabs_fofa.tk_table.delete(item) for item in
             self.tk_tabs.tk_tabs_fofa.tk_table.get_children()]
        except:
            pass
        try:
            self.tk_tabs.tk_tabs_fofa.tk_label['text'] = f"正在fofa上查询{self.target}的相关信息......"
            data = get(fofa_url, timeout=10).json()
            if not data['results']:
                self.tk_tabs.tk_tabs_fofa.tk_label['text'] = f"fofa查询完毕，未查询到相关信息"
            else:
                self.tk_tabs.tk_tabs_fofa.tk_label['text'] = f"fofa查询完毕，双击可复制所选内容"
                for item in data['results']:
                    self.tk_tabs.tk_tabs_fofa.tk_table.insert("", END, values=[item[0], item[1],
                                                                               item[2] + " " + item[3] + " " + item[4],
                                                                               item[5], item[6]])
        except ReadTimeout:
            self.tk_tabs.tk_tabs_fofa.tk_label['text'] = f"查询FOFA信息超时!"
            return
        except BaseException:
            self.tk_tabs.tk_tabs_fofa.tk_label['text'] = "查询FOFA出错!请检查网络及FOFA配置！"
            return

    def __get_hunter(self):
        self.tk_tabs.tk_tabs_hunter.tk_label['text'] = f"正在鹰图上查询{self.target}的相关信息......"
        try:
            [self.tk_tabs.tk_tabs_hunter.tk_table.delete(item) for item in
             self.tk_tabs.tk_tabs_hunter.tk_table.get_children()]
        except:
            pass
        words = b64encode(bytes('ip="{}"'.format(self.target).encode())).decode()
        hunter_url = f"https://hunter.qianxin.com/openApi/search?username={self.tk_tabs.tk_tabs_config.hunter_username.get()}&api-key={self.tk_tabs.tk_tabs_config.hunter_key.get()}&search={words}&page=1&page_size=10&is_web=1"
        try:
            res = get(hunter_url, timeout=5).json()
            if res['code'] != 200:
                self.tk_tabs.tk_tabs_hunter.tk_label['text'] = "查询鹰图信息超时"
                return
            else:
                use_point = res['data']['consume_quota']
                left_point = res['data']['rest_quota']
                try:
                    self.tk_tabs.tk_tabs_hunter.tk_label['text'] = f"鹰图查询完毕！{use_point}， {left_point}，双击可复制所选内容"
                    for data in res['data']['arr']:
                        self.tk_tabs.tk_tabs_hunter.tk_table.insert("", END, values=[
                            data['url'],
                            data['port'],
                            str(data['web_title']) if data['web_title'] else "N/A",
                            data['domain'] if data['domain'] else "N/A",
                            str(data['status_code']),
                            data['os'] if data['os'] else "N/A",
                            data['country'] + data['province'] + data['city'],
                            data['isp']
                        ])

                except TypeError as e:
                    self.tk_tabs.tk_tabs_hunter.tk_label['text'] = f"{e}"
                    return

        except BaseException as e:
            self.tk_tabs.tk_tabs_hunter.tk_label['text'] = f"查询鹰图信息失败!错误信息为：{e}"
            return

    def __get_weibu(self):
        self.tk_tabs.tk_tabs_weibu.tk_label['text'] = f"正在微步上查询{self.target}的相关信息......"
        try:
            [self.tk_tabs.tk_tabs_weibu.tk_table.delete(item) for item in
             self.tk_tabs.tk_tabs_weibu.tk_table.get_children()]
        except:
            pass
        weibu_url = "https://api.threatbook.cn/v3/scene/ip_reputation"
        query = {
            "apikey": self.tk_tabs.tk_tabs_config.weibu_key.get(),
            "resource": self.target,
            "lang": "zh"
        }
        try:
            res = post(url=weibu_url, params=query, timeout=5).json()
            print(res)
            data = res['data'][self.target]
            self.tk_tabs.tk_tabs_weibu.tk_label['text'] = f"微步查询完毕，双击可复制所选内容"
            target_judgments = ""
            for item in data['judgments']:
                target_judgments += item + ","
            target_tags = ""
            for item in data['tags_classes']:
                for tag in item['tags']:
                    target_tags += tag + ","
            self.tk_tabs.tk_tabs_weibu.tk_table.insert("", END, values=[
                data['severity'],
                target_judgments[:-1],
                target_tags[:-1],
                data['basic']['carrier'],
                data['basic']['location']['country'] + " " + data['basic']['location']['province'] +
                data['basic']['location']['city'],
                data['scene'],
                data['confidence_level']
            ])
        except TimeoutError as e:
            self.tk_tabs.tk_tabs_weibu.tk_label['text'] = f"微步查询失败！错误信息为：{e}"
            return
        except KeyError:
            self.tk_tabs.tk_tabs_weibu.tk_label['text'] = f"微步查询失败！可能是每日API请求次数已达上限"
            return


    def __get_0zone(self):
        self.tk_tabs.tk_tabs_0zone.tk_label['text'] = f"正在0zone上查询{self.target}的相关信息......"
        try:
            [self.tk_tabs.tk_tabs_0zone.tk_table.delete(item) for item in
             self.tk_tabs.tk_tabs_0zone.tk_table.get_children()]
        except:
            pass
        url = "https://0.zone/api/data/"
        query = {
            "title": f"ip={self.target}",
            "title_type": "site",
            "page": 1,
            "pagesize": 10,
            "zone_key_id": "{}".format(self.tk_tabs.tk_tabs_config.zone_key.get())
        }
        try:
            data = post(url=url, data=query, timeout=5).json()
            if data['code'] == 1:
                self.tk_tabs.tk_tabs_0zone.tk_label['text'] = f"查询出错，错误信息为: {data['message']}"
                return
            if not data['data']:
                self.tk_tabs.tk_tabs_0zone.tk_label['text'] = "没有在0zero平台查询到相关信息!"
                return
            self.tk_tabs.tk_tabs_0zone.tk_label['text'] = "微步查询完毕，双击可复制所选内容"
            for item in data['data']:
                self.tk_tabs.tk_tabs_0zone.tk_table.insert("", END, values=[
                    item["ip"] + ":" + item["port"],
                    item["url"] if item["url"] else "N/A",
                    item["title"] if item["title"] else "N/A",
                    item["os"] if item["os"] else "N/A",
                    item["component"] if item["component"] else "N/A",
                    item["operator"] if item["operator"] else "N/A",
                    item["protocol"] if item["protocol"] else "N/A"
                ])
        except TimeoutError:
            self.tk_tabs.tk_tabs_0zone.tk_label['text'] = "查询0zone信息超时"
            return
        except BaseException as e:
            self.tk_tabs.tk_tabs_0zone.tk_label['text'] = f"查询0zone信息失败！错误信息为：{e}"
            return

    def __get_shodan(self):
        self.tk_tabs.tk_tabs_shodan.tk_label['text'] = f"正在shodan上查询{self.target}的相关信息......"
        try:
            [self.tk_tabs.tk_tabs_shodan.tk_table.delete(item) for item in
             self.tk_tabs.tk_tabs_shodan.tk_table.get_children()]
        except:
            pass
        url = f"https://api.shodan.io/shodan/host/{self.target}?key={self.tk_tabs.tk_tabs_config.shodan_key.get()}"
        try:
            data = get(url, timeout=5).json()
            if 'error' in data:
                self.tk_tabs.tk_tabs_shodan.tk_label['text'] = f"没有在shodan上查询到 {self.target} 的相关信息"
            else:
                # ip
                try:
                    ip = data['ip_str']
                except:
                    ip = "N/A"
                # 端口
                try:
                    target_port = ""
                    for item in data['ports']:
                        target_port += str(item) + "、"
                except:
                    target_port = "N/A"
                try:
                    target_isp = data['isp']
                except:
                    target_isp = "N/A"
                try:
                    for host in data['domains']:
                        for domain in data['hostnames']:
                            self.tk_tabs.tk_tabs_shodan.tk_table.insert("", END, values=[ip, target_port[:-1], host, domain, target_isp])
                except:
                    self.tk_tabs.tk_tabs_shodan.tk_table.insert("", END,
                                                                values=[ip, target_port[:-1], "N/A", "N/A", target_isp])
                self.tk_tabs.tk_tabs_shodan.tk_label['text'] = "shodan查询完毕，双击可复制所选内容"
        except TimeoutError:
            self.tk_tabs.tk_tabs_shodan.tk_label['text'] = "查询shodan信息超时！"
            return
        except BaseException as e:
            self.tk_tabs.tk_tabs_shodan.tk_label['text'] = f"查询shodan信息失败！错误信息为：{e}"
            return

    def __get_zoomeye(self):
        self.tk_tabs.tk_tabs_zoomeye.tk_label['text'] = f"正在zoomeye上查询{self.target}的相关信息......"
        try:
            [self.tk_tabs.tk_tabs_zoomeye.tk_table.delete(item) for item in
             self.tk_tabs.tk_tabs_zoomeye.tk_table.get_children()]
        except:
            pass
        url = "https://api.zoomeye.org/host/search?query=%s" % self.target
        headers = {
            "API-KEY": self.tk_tabs.tk_tabs_config.zoomeye_key.get()
        }
        try:
            data = get(url=url, headers=headers, timeout=5).json()
            if data['total'] != 0:
                for item in data['matches']:
                    self.tk_tabs.tk_tabs_zoomeye.tk_table.insert("", END, values=[
                        item['ip'],
                        str(item['portinfo']['port']) if item['portinfo']['port'] else "",
                        item['portinfo']['app'] if item['portinfo']['app'] else "",
                        item['portinfo']['title'][0] if item['portinfo']['title'] is not None else "",
                        item['portinfo']['service'] if item['portinfo']['service'] else "",
                    ])
                self.tk_tabs.tk_tabs_zoomeye.tk_label['text'] = "zoomeye查询完毕，双击可复制所选内容"
            else:
                self.tk_tabs.tk_tabs_zoomeye.tk_label['text'] = f"没有在zoomeye上查询到 {self.target} 的相关信息"
        except TimeoutError:
            self.tk_tabs.tk_tabs_zoomeye.tk_label['text'] = "查询zoomeye信息超时！"
            return
        except BaseException as e:
            self.tk_tabs.tk_tabs_zoomeye.tk_label['text'] = f"查询zoomeye信息失败！错误信息为：{e}"
            return

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
        if not cfg.has_section('0zone'):
            cfg.add_section('0zone')
        cfg.set('0zone', 'apikey', self.tk_tabs.tk_tabs_config.tk_label_frame_0zone.tk_input_0zone_key.get())
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
        self.tk_tabs_fofa = Frame_results(self, attribute={'host': 250, '标题': 250, '地理位置': 200, '服务名': 150, '协议': 50})
        self.add(self.tk_tabs_fofa, text="FOFA")

        self.tk_tabs_hunter = Frame_results(self, attribute={'url': 250, '端口': 50, "网页标题": 150, '域名': 200, '状态码': 60,
                                                             "操作系统": 70, '归属地': 60, "运营商": 60})
        self.add(self.tk_tabs_hunter, text="鹰图")

        self.tk_tabs_weibu = Frame_results(self,
                                           attribute={'威胁等级': 70, 'IP类型判断': 230, '威胁类型': 120, '运营商': 120, '地理位置': 120,
                                                      "场景": 120, "情报可信度": 120})
        self.add(self.tk_tabs_weibu, text="微步")

        self.tk_tabs_0zone = Frame_results(self, attribute={'host': 200, 'url': 250, '网页标题': 230, '操作系统': 70, '服务器': 60,
                                                            "运营商": 70, "协议": 60})
        self.add(self.tk_tabs_0zone, text="0zone")

        self.tk_tabs_shodan = Frame_results(self,
                                            attribute={'IP': 100, '开放的端口': 150, '域名': 150, '子域名': 200, '运营商': 320})
        self.add(self.tk_tabs_shodan, text="shodan")

        self.tk_tabs_zoomeye = Frame_results(self,
                                             attribute={'IP': 100, '端口': 50, '服务标题': 250, '应用': 250, '协议': 250, })
        self.add(self.tk_tabs_zoomeye, text="zoomeye")

        self.tk_tabs_config = Frame_config(self)
        self.add(self.tk_tabs_config, text="配置页")

        self.place(x=10, y=40, width=980, height=500)


# 单个结果页的frame-fofa
class Frame_results(Frame):
    def __init__(self, parent, attribute: dict):
        super().__init__(parent)
        self.attribute = attribute
        self.__frame()
        self.tk_label = self.__tk_label()
        self.tk_table = self.__tk_table()

    def __frame(self):
        self.place(x=10, y=40, width=960, height=480)

    def __tk_label(self):
        label = Label(
            self,
            borderwidth=3,
            relief="sunken",
            font=('微软雅黑', 15, 'bold'),
            anchor="n"
        )
        label.place(x=10, y=10, width=958, height=30)
        label.bind('<Double-1>', self.__get_value_label)
        return label

    def __tk_table(self):
        y_scroll = tkinter.Scrollbar(
            self,
            orient=VERTICAL,
        )
        table = Treeview(
            self,
            show="headings",
            columns=list(self.attribute),
            yscrollcommand=y_scroll.set,
            padding=5,
        )
        for text, width in self.attribute.items():  # 批量设置列属性
            table.heading(text, text=text, anchor='w')
            table.column(text, anchor='w', width=width, stretch=False)  # stretch 不自动拉伸
        y_scroll.config(command=table.yview)
        y_scroll.pack(side=RIGHT, fill=Y)
        table.place(x=10, y=40, width=950, height=420)
        table.bind('<Double-1>', self.__get_value_table)
        return table

    def __get_value_table(self, event):
        root.clipboard_clear()
        selections = self.tk_table.selection()
        values = {}
        try:
            for row in selections:
                values = self.tk_table.item(row, 'values')
            column = self.tk_table.identify_column(event.x)
            root.clipboard_append(values[int(column.replace("#", "")) - 1])
            self.tk_label['text'] = f'{values[int(column.replace("#", "")) - 1]}复制成功！' if values[int(column.replace("#",
                                                                                                                    "")) - 1] != "" else "啥都没有哦"
        except:
            return

    def __get_value_label(self, event):
        try:
            root.clipboard_clear()
            root.clipboard_append(self.tk_label['text'])
        except:
            return


# 配置页的总frame
class Frame_config(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.__frame()
        self.__check_config()
        self.tk_label_frame_fofa = Frame_config_fofa(self, self.fofa_mail, self.fofa_key)
        self.tk_label_frame_hunter = Frame_config_hunter(self, self.hunter_username, self.hunter_key)
        self.tk_label_frame_weibu = Frame_config_weibu(self, self.weibu_key)
        self.tk_label_frame_0zone = Frame_config_0zone(self, self.zone_key)
        self.tk_label_frame_shodan = Frame_config_shodan(self, self.shodan_key)
        self.tk_label_frame_zoomeye = Frame_config_zoomeye(self, self.zoomeye_key)
        self.__self_label_tips()

    def __frame(self):
        self.configure()
        self.place(x=10, y=40, width=985, height=480)

    def __self_label_tips(self):
        label = Label(self, anchor="nw", wraplength=280, justify="left", font=('微软雅黑', 13, 'bold'), text="""
fofa APIKEY获取地址：https://fofa.info/personalData\n\n\n\n
鹰图APIKEY获取地址：https://hunter.qianxin.com/home/userInfo\n\n\n\n
微步APIKEY获取地址：https://x.threatbook.cn/v5/myApi\n\n
0zero APIKEY获取地址：https://0.zone/applyParticulars?type=site\n\n
shodan APIKEY获取地址：https://account.shodan.io/\n\n
zoomeye APIKEY获取地址：https://www.zoomeye.org/profile\n
""")
        label.place(x=680, y=10, width=295, height=450)

    def __check_config(self):
        read_ok = cfg.read('config.ini', encoding='utf-8')
        if not read_ok:
            tkinter.messagebox.showinfo(title="info",
                                        message=f"未在当前目录检测到config.ini，请在config页进行配置，进行一次查询后会将配置保存到当前目录的config.ini，之后即可自动读取配置")
            self.fofa_mail = StringVar(value="")
            self.fofa_key = StringVar(value="")
            self.hunter_username = StringVar(value="")
            self.hunter_key = StringVar(value="")
            self.weibu_key = StringVar(value="")
            self.zone_key = StringVar(value="")
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
            # 0zone
            try:
                self.zone_key = StringVar(value=cfg['0zone']['apikey'])
            except KeyError:
                self.zone_key = StringVar(value="")
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
        self.configure(text="fofa")
        self.place(x=10, y=10, width=655, height=90)

    def __tk_input_fofa_mail(self):
        ipt = Entry(self, textvariable=self.fofa_mail)
        ipt.place(x=80, y=0, width=560, height=30)
        return ipt

    def __tk_input_fofa_key(self):
        ipt = Entry(self, textvariable=self.fofa_key)
        ipt.place(x=80, y=35, width=560, height=30)
        return ipt

    def __tk_label_fofa_mail(self):
        label = Label(self, text="邮箱")
        label.place(x=10, y=0, width=70, height=30)
        return label

    def __tk_label_fofa_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=35, width=70, height=30)
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
        self.configure(text="鹰图")
        self.place(x=10, y=110, width=655, height=90)

    def __tk_input_hunter_username(self):
        ipt = Entry(self, textvariable=self.hunter_username)
        ipt.place(x=80, y=0, width=560, height=30)
        return ipt

    def __tk_input_hunter_key(self):
        ipt = Entry(self, textvariable=self.hunter_key)
        ipt.place(x=80, y=35, width=560, height=30)
        return ipt

    def __tk_label_hunter_username(self):
        label = Label(self, text="用户名")
        label.place(x=10, y=0, width=70, height=30)
        return label

    def __tk_label_hunter_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=35, width=70, height=30)
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
        self.configure(text="微步")
        self.place(x=10, y=210, width=655, height=55)

    def __tk_input_weibu_key(self):
        ipt = Entry(self, textvariable=self.weibu_key)
        ipt.place(x=80, y=0, width=560, height=30)
        return ipt

    def __tk_label_weibu_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=0, width=70, height=30)
        return label


# 配置页的0zone frame
class Frame_config_0zone(LabelFrame):
    def __init__(self, parent, zone_key):
        super().__init__(parent)
        self.zone_key = zone_key
        self.__frame()
        self.tk_input_0zone_key = self.__tk_input_0zone_key()
        self.tk_label_0zone_key = self.__tk_label_0zone_key()

    def __frame(self):
        self.configure(text="0zone")
        self.place(x=10, y=275, width=655, height=55)

    def __tk_input_0zone_key(self):
        ipt = Entry(self, textvariable=self.zone_key)
        ipt.place(x=80, y=0, width=560, height=30)
        return ipt

    def __tk_label_0zone_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=0, width=70, height=30)
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
        self.configure(text="shodan")
        self.place(x=10, y=340, width=655, height=55)

    def __tk_input_shodan_key(self):
        ipt = Entry(self, textvariable=self.shodan_key)
        ipt.place(x=80, y=0, width=560, height=30)
        return ipt

    def __tk_label_shodan_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=0, width=70, height=30)
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
        self.configure(text="zoomeye")
        self.place(x=10, y=405, width=655, height=55)

    def __tk_input_zoomeye_key(self):
        ipt = Entry(self, textvariable=self.zoomeye_key)
        ipt.place(x=80, y=0, width=560, height=30)
        return ipt

    def __tk_label_zoomeye_key(self):
        label = Label(self, text="APIKEY")
        label.place(x=10, y=0, width=70, height=30)
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
