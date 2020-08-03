import shelve
import datetime
import random
import urwid
import math


palette = [
    ('very_healthy', 'light green,bold', ''),
    ('healthy', 'dark green,bold', ''),
    ('ok', 'white', ''),
    ('thirsty', 'yellow,bold', ''),
    ('very_thirsty', 'brown,bold', ''),
    # ('moribund', '', '', '', '#60d', ''),
    # ('dead', 'black','#60d', ''),
    # TODO: refine these colors for 256 color display!
]

STATUS = ('very_healthy', 'healthy', 'ok', 'thirsty',
          'very_thirsty', 'moribund', 'dead')

saved_habits = shelve.open('habits')


class Habit:
    def __init__(self, title, rate):
        # TODO: write tests for correct health output
        self.last_fed = datetime.date.today() - datetime.timedelta(days=10)
        #self.last_fed = datetime.date.today()
        self.rate = rate
        self.title = title
        self.update_status()
        self.notes = []

    def update_status(self):
        today = datetime.date.today()
        days_since_fed = today - self.last_fed
        self.status = STATUS[min(math.floor(
            days_since_fed.days / self.rate), len(STATUS) - 1)]

    def update_habit(self, update_time, update):
        if update:
            self.last_fed = update_time
            self.update_status()


class HabitList:
    def __init__(self):
        self.habits = saved_habits.get('habits', {})

    def add_habit(self, name, rate):
        new_habit = Habit(name, rate)
        if name in self.habits:
            return 'Entry already exists.'
        self.habits[name] = new_habit
        self.save_habits()

    def get_habit_status(self):
        for habit in self.habits.values():
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
    return urwid.BoxAdapter(urwid.ListBox(urwid.SimpleFocusListWalker(body)), height=5)


def get_urwid_habits(habit_list):
    habits = []
    for habit in habit_list:
        habits.append(urwid.AttrMap(urwid.Text(habit.title), habit.status))
    return urwid.Pile(habits)


def quit():
    raise urwid.ExitMainLoop()


class UpdateAllHabitsAsker():

    def __init__(self, habits):
        self.day_to_update = None
        content.original_widget = self.ask()
        self.current_habit = None
        self.habits = list(habits.keys())

    def ask(self):
        return selection_menu('Current day or yesterday?', [
            'yesterday', 'today'], self.get_day)

    def handle_update(self, button, choice):
        update = choice == 'Yes'
        my_habits.habits[self.current_habit].update_habit(
            self.day_to_update, update)
        self.update_habits()

    def get_day(self, button, choice):
        day_key = {
            'yesterday': datetime.date.today() - datetime.timedelta(days=1),
            'today': datetime.date.today()
        }
        self.day_to_update = day_key[choice]
        self.update_habits()

    def update_habits(self):
        if self.habits:
            habit_to_update = self.habits.pop()
            self.current_habit = habit_to_update
            answers = ["Yes", "No"]
            buttons = [urwid.Text(habit_to_update), urwid.Divider()]
            for answer in answers:
                button = urwid.Button(answer)
                urwid.connect_signal(
                    button, 'click', self.handle_update, answer)
                buttons.append(urwid.AttrMap(
                    button, None, focus_map='reversed'))
            content.original_widget = urwid.BoxAdapter(urwid.ListBox(
                urwid.SimpleFocusListWalker(buttons)), height=5)
        else:
            content.original_widget = get_main_habit_list()


class AddHabitEditBox(urwid.Filler):
    name = None
    rate = None

    def keypress(self, size, key):
        # TODO: handle bad input for 'rate'
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
            self.original_widget = urwid.Edit(
                f'Thanks! You have added {self.name} with a rate of {self.rate} days.\nPress return to go back to the main list.')
            my_habits.add_habit(self.name, self.rate)
            return super(AddHabitEditBox, self).keypress(size, key)
        content.original_widget = get_main_habit_list()


def ask_new_habit():
    habit_input = urwid.Edit(u'Add habit?\n')
    edit_box_habitname = urwid.BoxAdapter(
        AddHabitEditBox(habit_input), height=5)
    content.original_widget = edit_box_habitname


def ask_update_all_habits():
    UpdateAllHabitsAsker(my_habits.habits)


def handle_input(key):
    # TODO: fix unexpected input problems
    key = key.lower()
    if key == 'q':
        quit()
    if key == 'a':
        ask_new_habit()
    if key == 'u':
        ask_update_all_habits()


def get_main_habit_list():
    return get_urwid_habits(my_habits.habits.values())


my_habits = HabitList()


header_text = urwid.Text(u'HABITS')
instructions = urwid.Text(u'(u)pdate (a)dd (e)dit (d)elete (q)uit')
content = urwid.Filler(get_main_habit_list(), valign='middle')
layout = urwid.Frame(body=content, header=header_text, footer=instructions)
loop = urwid.MainLoop(layout, palette=palette, unhandled_input=handle_input)
loop.screen.set_terminal_properties(colors=256)
loop.run()
