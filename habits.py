import shelve
import datetime, random
import urwid
import math


palette = [
    ('very_healthy', 'light green,bold', ''),
    ('healthy', 'dark green,bold',''),
    ('ok', 'white',''),
    ('thirsty', 'yellow,bold', ''),
    ('very_thirsty', 'brown,bold', ''),
    #('moribund', '', '', '', '#60d', ''),
    #('dead', 'black','#60d', ''),
    # TODO: refine these colors for 256 color display! 
    ]

STATUS = ('very_healthy', 'healthy', 'ok', 'thirsty', 'very_thirsty', 'moribund', 'dead')

saved_habits = shelve.open('habits')

class Habit:
    def __init__(self, title, rate):
        # TODO: write tests for correct health output
        #self.last_fed = datetime.date.today() - datetime.timedelta(days=10)
        self.last_fed = datetime.date.today()
        self.rate = rate
        self.title = title
        self.update_status()
        self.notes = []

    def update_status(self):
        today = datetime.date.today()
        days_since_fed = today - self.last_fed
        self.status = STATUS[min(math.floor(days_since_fed.days / self.rate), len(STATUS) - 1)]

    def update_habit(self, update):
        self.last_fed = datetime.date.today()
        self.status = STATUS[0]

class HabitList:
    def __init__(self):
        self.habits = saved_habits.get('habits', []) 

    def add_habit(self, name, rate):
        new_habit = Habit(name, rate)
        self.habits.append(new_habit)
        self.save_habits()

    def update_all_habits(self, answers, day):
        for i, habit in enumerate(self.habits):
            if answers[i]:
                habit.update_habit()
        self.save_habits()

    def get_habit_status(self):
        for habit in self.habits:
            habit.update_status()
        self.save_habits()
    
    def get_habits(self):
        return self.habits

    def save_habits(self):
        saved_habits['habits'] = self.habits

def selection_menu(title, choices, action):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', action, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def get_urwid_habits(habit_list):
    habits = []
    for habit in habit_list:
        habits.append(urwid.AttrMap(urwid.Text(habit.title), habit.status))
    return urwid.Pile(habits)

def quit():
    raise urwid.ExitMainLoop()

class AddHabitEditBox(urwid.Filler):
    name = False
    rate = False
    def keypress(self, size, key):
        #TODO: handle bad input for 'rate'
        if key != 'enter':
            if self.name and self.rate:
                self.original_widget.edit_text = ''
            return super(AddHabitEditBox, self).keypress(size, key)
        if not self.name:
            self.name = self.original_widget.edit_text
            self.original_widget = urwid.Edit(u'Set your rate...\n')
            return super(AddHabitEditBox, self).keypress(size, key)
        if not self.rate:
            self.rate = int(self.original_widget.edit_text)           
            self.original_widget = urwid.Edit(f'Thanks! You have added {self.name} with a rate of {self.rate} days.\nPress return to go back to the main list.')
            my_habits.add_habit(self.name, self.rate)
            return super(AddHabitEditBox, self).keypress(size,key)
        content.original_widget = get_main_habit_list()

def ask_new_habit():
    habit_input = urwid.Edit(u'Add habit?\n')
    edit_box_habitname = urwid.BoxAdapter(AddHabitEditBox(habit_input), height=5)
    content.original_widget = edit_box_habitname

def handle_input(key):
    key = key.lower()
    if key == 'q':
        quit()
    if key == 'a':
        ask_new_habit()

def get_main_habit_list():
    return get_urwid_habits(my_habits.habits)

my_habits = HabitList()

header_text = urwid.Text(u'HABITS')
instructions = urwid.Text(u'(u)pdate (a)dd (e)dit (d)elete (q)uit')
content = urwid.Filler(get_main_habit_list(), valign='middle')
layout = urwid.Frame(body=content, header=header_text, footer=instructions)
loop = urwid.MainLoop(layout, palette=palette, unhandled_input=handle_input)
loop.screen.set_terminal_properties(colors=256)
loop.run()