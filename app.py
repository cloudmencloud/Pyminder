import tkinter as tk
import datetime as dt
import os
import json as js


class App(tk.Tk):
    class AboutWin(tk.Toplevel):
        def __init__(self, theme,*args, **kargs):
            super().__init__(*args, **kargs)
            self.title("About Pyminder")
            self.resizable(0, 0)
            self.geometry("300x250")
            self.theme = theme
            self.canv = tk.Canvas(self, bg=theme['bg'])
            self.img = tk.PhotoImage(file='./pyminder.png', width=300, height=125)
            self.canv.create_image((150, 50), image=self.img)
            self.canv.create_text((150, 125), fill=self.theme['fg'], text="Made for the FurDevs code challenege #4")
            self.canv.create_text((150, 145), fill=self.theme['fg'], text="Submitted some time between 18/8/21 to 20/8/21")

            self.canv.pack(fill='both',expand=1)
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.iconphoto(True, tk.PhotoImage(file='./PM2.png'))
        self.notif = Notify(default_notification_title="Pyminder",default_notification_message="Reminder")
        self.title("PyMinder")
        Config.setup_config('./config.json')
        self.data = Config.load_config('./config.json')
        try:
            self.tasks = self.data['tasks']
            self.theme = self.data['theme']
        except KeyError:
            print('Unable to load data, reverting to defaults')
            self.tasks = []
            self.theme = {'fg':'#b7b2b3', 'bg':'#0f0e0e'}
        self.font = ('Helventica','16')
        self.canvas = tk.Canvas(self)
        self.geometry('400x300')
        self.resizable(0, 0)
        self.up_frame = TaskFrame(self.canvas, self.theme, self.tasks)
        self.floatbtn = tk.Button(self.canvas, fg=self.theme['fg'], bg=self.theme['bg'], text='+', font=self.font)
        self.floatbtn2 = tk.Button(self.canvas, fg=self.theme['fg'], bg=self.theme['bg'], text='-', font=self.font)
        self.infobtn = tk.Button(self.canvas, fg=self.theme['fg'], bg=self.theme['bg'], text='I', font=self.font)
        self.floatbtn.configure(command=self.new_task)
        self.floatbtn2.configure(command=self.remove_task)
        self.infobtn.configure(command=self.info_win)
        self.canvas.pack(expand=1, fill='both', anchor='nw')
        self.canvas.create_window((0, 0), window=self.up_frame, anchor='nw',tags='yes')
        self.b_x = self.winfo_width() // 6
        self.b_y = self.winfo_height() // 10
        self.after(100, self.scale)
        self.taskwin = None
        self.infowin = None
        self.task = {}
        self.check_if_task()
        self.up_frame.update_list()
        self.check_tasks()
    def info_win(self):
        if self.infowin != None:
            self.infowin.destroy()
            self.infowin = None
        else:
            self.infowin = self.AboutWin(self.theme, master=self)
    def check_tasks(self):
        d_now = dt.datetime.now()
        for task in self.tasks:
            t_due = task['due']
            d_task = dt.datetime(2021, t_due['m'], t_due['d'], t_due['h'], t_due['mn'])
            if d_task < d_now:
                if not task['done']:
                    self.notif.message = task['name']
                    self.notif.send()
                    task['done'] = not task['done']
                    self.tasks[self.tasks.index(task)] = task
                    self.data['tasks'] = self.tasks
                    Config.save_config('./config.json',self.data)
                    continue
                else:
                    print(task)
        self.after(1000, self.check_tasks)
    def new_task(self):
        if self.taskwin == None:
            self.taskwin = NewTaskWin(self.theme, master=self)
        else: 
            self.taskwin.destroy()
            self.taskwin = None
    def remove_task(self):
        s = self.up_frame.up_list.selection_get()
        i = self.up_frame.up_list.curselection()[0]
        self.tasks.pop(i)
        self.up_frame.up_list.delete(i)
        self.data['tasks'] = self.tasks
        Config.save_config('./config.json', self.data)
        print(s)
    def check_if_task(self):
        try:
            if self.taskwin != None:
                self.task['name'] = self.taskwin.task.name
                dat  = self.taskwin.task.dati
                due = {'m':dat.month, 'd':dat.day, 'h':dat.hour, 'mn':dat.minute}
                self.task['due'] = due
                self.task['done'] = False
                
                self.tasks.append(self.task)
                self.data['tasks'] = self.tasks
                self.up_frame.update_list()
                Config.save_config('./config.json', self.data)
            else:
                pass
        except Exception as e:
            pass
    def scale(self):
        l = 'Upcoming Activities'
        self.b_x = self.canvas.winfo_width() - self.canvas.winfo_width() // 8
        self.b_y = self.canvas.winfo_height() - self.canvas.winfo_height() // 10
        self.canvas.create_rectangle((0, 0, self.canvas.winfo_width(), self.canvas.winfo_height()), fill=self.theme['bg'])
        self.canvas.create_window((5, 5), window=self.up_frame, anchor='nw',tags='yes', width=2*len(l)+self.b_x, height=self.b_y)
        self.canvas.create_window((self.b_x, self.b_y), window=self.floatbtn, width=30, height=30,tags='float')
        self.canvas.create_window((self.b_x-300, self.b_y), window=self.floatbtn2, width=30, height=30,tags='float')
        self.canvas.create_window((25, 20), window=self.infobtn, width=30, height=30,tags='float')
        self.after(100, self.scale)
    def run(self):
        self.mainloop()
class Config:
    @staticmethod
    def setup_config(fp):
        if not os.path.exists(fp):
            print('CFG file not found, creating')
            with open(fp, 'w') as cfg:
                cfg.write('{}')
                print('Created CFG file')
        else:
            print('CFG file found, loading it')
    @staticmethod
    def load_config(fp):
        if os.path.exists(fp):
            with open(fp, 'r') as cfg:
                print('Loading CFG file')
                data = js.load(fp=cfg)
                print(data)
                return data
    @staticmethod
    def save_config(fp, data):
        if os.path.exists(fp):
            with open(fp, 'w') as cfg:
                print("Saving to CFG file")
                js.dump(data, cfg, indent=4)
                print("Saved")
class TaskFrame(tk.Frame):
    def __init__(self, parent, theme, upc,*args, **kargs):
        super().__init__(parent, *args, **kargs)
        
        self.upcoming = upc
        self.up_lb = tk.Label(self, fg=theme['fg'], bg=theme['bg'], text='Upcoming Activities')
        self.up_lb.pack(fill='both', expand=1)
        self.up_list = tk.Listbox(self,fg=theme['fg'],bg=theme['bg'], borderwidth=0)
        self.up_list.pack(fill='both', expand=1)
    def update_list(self):
        self.up_list.delete(0, 'end')
        for u in self.upcoming:
            d = dt.datetime(dt.date.today().year, u['due']['m'], u['due']['d'], u['due']['h'], u['due']['mn'], 0)
            if u['done']:
                self.up_list.insert('end', '\u0336'.join(f"{u['name']}: due {d}  (in {u['due']['d'] - dt.datetime.today().day}d, {u['due']['h'] - dt.datetime.today().hour}h)") + '\u0336')
            else:
                self.up_list.insert('end', f"{u['name']}: due {d}  (in {u['due']['d'] - dt.datetime.today().day}d, {u['due']['h'] - dt.datetime.today().hour}h)")
class NewTaskWin(tk.Toplevel):
    class DateEntry(tk.Canvas):
        def __init__(self, master, theme, *args, **kargs):
            super().__init__(master, *args, **kargs)
            self.date = dt.datetime.today()
            
            self.theme = theme
            self.months = {"Jan.":31, "Feb.":28, "Mar.":30, "Apr.":30, "May.":31, "Jun.":30, "Jul.":31, "Aug.":31, "Sept.":30, "Oct.":31, "Nov.":30, "Dec.":31}
            
            self.day = self.date.day
            self.month = list(self.months.keys())[self.date.month-1]
            self.year = self.date.year
            
            self.min = self.date.minute
            self.hour = self.date.hour

            self.i = list(self.months.items())[self.date.month-1][1]
            print(self.i)

            self.m_btn_up = tk.Button(self, bg=theme['bg'], fg=theme['fg'], text="^", command=self.scroll_month_up)
            self.m_btn_down = tk.Button(self, bg=theme['bg'], fg=theme['fg'], text="v", command=self.scroll_month_down)
            self.m_btn_down.pack()
            self.m_btn_up.pack()
            
            self.d_btn_up = tk.Button(self, bg=theme['bg'], fg=theme['fg'], text="^", command=self.scroll_day_up)
            self.d_btn_down = tk.Button(self, bg=theme['bg'], fg=theme['fg'], text="v", command=self.scroll_day_down)
            self.d_btn_down.pack()
            self.d_btn_up.pack()
            
            self.h_btn_up = tk.Button(self, bg=theme['bg'], fg=theme['fg'], text="^", command=self.scroll_hour_up)
            self.h_btn_down = tk.Button(self, bg=theme['bg'], fg=theme['fg'], text="v", command=self.scroll_hour_down)
            self.h_btn_down.pack()
            self.h_btn_up.pack()

            self.mn_btn_up = tk.Button(self, bg=theme['bg'], fg=theme['fg'], text="^", command=self.scroll_min_up)
            self.mn_btn_down = tk.Button(self, bg=theme['bg'], fg=theme['fg'], text="v", command=self.scroll_min_down)
            self.mn_btn_down.pack()
            self.mn_btn_up.pack()
            
            self.done_btn = tk.Button(self, bg=theme['bg'], fg=theme['fg'],text='Done', command=self.done)
            self.done_btn.pack()

            self.task_entry = tk.Entry(self, bg=theme['bg'], fg=theme['fg'])
            self.task_entry.insert('end', "Task Name:")
            self.task_entry.pack()
            
            self.update_canv()
        def scroll_min_up(self):
            if self.min < 60:
                self.min += 1
            else:
                self.min = 0
        def scroll_min_down(self):
            if self.min > 2:
                self.min -= 1
            else:
                self.min = 60
        def done(self):
            l = list(self.months.keys())
            dait = dt.datetime(self.year, l.index(self.month)-1, self.day, self.hour, self.min, 0)
            self.master.task = Task(self.task_entry.get(), dait, False)
            self.master.master.check_if_task()
            self.master.master.taskwin = None
            self.master.destroy()
        def scroll_hour_up(self):
            if self.hour < 24:
                self.hour += 1 
            else:
                self.hour = 0
        def scroll_hour_down(self):
            if self.hour >= 2:
                self.hour -= 1
            else:
                self.hour = 24
        def scroll_month_up(self):
            l = list(self.months.keys())
            if self.i < len(self.months.items())-1:
                self.i += 1
            else:
                self.i = 0
            self.month = l[l.index(self.month)-1]
        def scroll_month_down(self):
            l = list(self.months.keys())
            if self.i >= 0:
                self.i -= 1
            else:
                self.i = len(self.months.keys())
            self.month = l[l.index(self.month)-1]
        def scroll_day_up(self):
            l = list(self.months.keys())
            indx = l.index(self.month)-1
            if self.day < int(list(self.months.items())[indx][1]):
                self.day += 1
            else:
                self.day = 1
        def scroll_day_down(self):
            l = list(self.months.keys())
            indx = l.index(self.month)-1
            if self.day >= 2:
                self.day -= 1
            else:
                self.day = int(list(self.months.items())[indx][1])
        def update_canv(self):
            m_text_x = self.winfo_width() -(len(str(self.month))+ self.winfo_width() //1.5)
            md_text_y = self.winfo_height() - self.winfo_height()//1.75
            d_text_x = self.winfo_width() - (len(str(self.day)) + self.winfo_width() //1.25)
            h_text_x = self.winfo_width() - (len(str(self.hour))+ self.winfo_width() // 2.25)
            mn_text_x = self.winfo_width() - (len(str(self.min))+ self.winfo_width() // 2.75)
            self.create_rectangle((0, 0, self.winfo_width(), self.winfo_height()),fill=self.theme['bg'])
            self.create_text((d_text_x, md_text_y), text=f"Day:\n{str(self.day)}",fill=self.theme['fg'])
            self.create_text((m_text_x+10, md_text_y), text=f"Month:\n{str(self.month)}",fill=self.theme['fg'])
            self.create_text((h_text_x, md_text_y), text=f"Hour:\n{str(self.hour)}",fill=self.theme['fg'])
            self.create_text((mn_text_x+30, md_text_y), text=f"Minu:\n{str(self.min)}",fill=self.theme['fg'])
            self.create_window((m_text_x+10, md_text_y - 20), window=self.m_btn_up, width=len(str(self.month))*15, height=10)
            self.create_window((m_text_x+10, md_text_y + 20), window=self.m_btn_down, width=len(str(self.month))*15, height=10)
            self.create_window((d_text_x, md_text_y - 20), window=self.d_btn_up, width=len(str(self.day))*15, height=10)
            self.create_window((d_text_x, md_text_y + 20), window=self.d_btn_down, width=len(str(self.day))*15, height=10)
            self.create_window((self.winfo_width()//2, self.winfo_height()-20), height=20, width=len("done")*25,window=self.done_btn)
            self.create_window((h_text_x, md_text_y-20),window=self.h_btn_up, height=10, width=len(str(self.hour))*25)
            self.create_window((h_text_x, md_text_y+20),window=self.h_btn_down, height=10, width=len(str(self.hour))*25)
            self.create_window((mn_text_x+30, md_text_y-20),window=self.mn_btn_up, height=10, width=len(str(self.min))*25)
            self.create_window((mn_text_x+30, md_text_y+20),window=self.mn_btn_down, height=10, width=len(str(self.min))*25)
            self.create_window((self.winfo_width()//2, md_text_y-45), window=self.task_entry, width=int(len(self.task_entry.get())*10.1), height=20)
            self.after(100, self.update_canv)
    def __init__(self, theme,*args, **kargs):
        super().__init__(*args, **kargs)
        self.theme = theme
        self.task = None
        self.title("New Task")
        
        self.resizable(0, 0)
        self.geometry('300x200')
        self.configure(background=theme['bg'])
        self.date_entry = self.DateEntry(self, self.theme)
        self.date_entry.pack(fill='both',expand=1)
class Task:
    def __init__(self, name:str, dati:dt.datetime, done) -> None:
        self.name = name
        self.dati = dati
        self.done = done
App().run()