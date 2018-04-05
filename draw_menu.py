#!/usr/bin/env python3
import urwid

from get_menu_items import menu_items, exit_key, text_main_menu


def back_button():
    button = urwid.Button('Back...')

    def back(button):
        return top.back()

    urwid.connect_signal(button, 'click', back)
    return urwid.AttrMap(button, 'bg', focus_map='reversed')


def apply_button():
    button = urwid.Button('Apply...')

    def apply(button):
        return top.apply_script()

    urwid.connect_signal(button, 'click', apply)
    return urwid.AttrMap(button, 'bg', focus_map='reversed')


def menu_btn_group(choices_checkbox, sel_all_btn=False, apply_btn=False):
    button_group = []
    if sel_all_btn:
        button = urwid.Button('Select all')

        def select_all(button):
            return [i.toggle_state() for i in choices_checkbox]

        urwid.connect_signal(button, 'click', select_all)
        button_group.append(urwid.AttrMap(button, 'bg', focus_map='reversed'))

    button_group.append(back_button())

    if apply_btn:
        button_group.append(apply_button())

    return urwid.GridFlow(button_group, 15, 1, 1, 'center')


def menu_button(caption, callback, script=""):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback, script if script else None)
    return urwid.AttrMap(button, 'bg', focus_map='reversed')


def sub_menu(caption, text, choices, checkbox, script):
    contents = menu(caption, text, choices, checkbox)
    contents.script = script

    def open_menu(button):
        return top.open_box(contents)

    return menu_button([caption, '...'], open_menu)


def menu(title, text, choices, checkbox, top_level=False):
    text = '' if not text else text
    body = [urwid.Text(title), urwid.Divider(), urwid.Text(text),
            urwid.Divider()]
    body.extend(choices)

    if not top_level:
        body.append(menu_btn_group(
            choices_checkbox=choices,
            sel_all_btn=checkbox,
            apply_btn=checkbox
        ))

    menu_obj = urwid.ListBox(urwid.SimpleFocusListWalker(body))
    menu_obj.checkbox = checkbox

    return menu_obj


def item_chosen(button, script=""):
    response = urwid.Text(['You chose ', button.label, '\n'])

    def back(button):
        return top.back()

    def apply_script(button):
        return top.apply_script()

    back_to_menu = menu_button('Back', back)
    apply = menu_button('Apply', apply_script)
    box = urwid.Filler(urwid.Pile([response, back_to_menu, apply]))
    box.script = script
    top.open_box(box)


def exit_program():
    raise urwid.ExitMainLoop()


def checkbox_button(caption):
    def check(button, new_state, value):
        return top.checkbox_changed(value, new_state)

    item = urwid.CheckBox(caption)
    urwid.connect_signal(item, 'change', check, caption)

    return item
    # return urwid.AttrMap(item, 'bg', focus_map='reversed')


def recursive(obj, checkbox=False):
    lst = []
    if isinstance(obj, dict):
        if obj["items"] is None:
            if checkbox:
                return checkbox_button(obj["name"])
            else:
                return menu_button(obj["name"], item_chosen, obj["script"])
        else:
            checkbox = True if obj.get("checkbox", 'n') == 'y' else False
            return sub_menu(obj["name"],
                            obj["text"],
                            recursive(obj["items"], checkbox),
                            checkbox,
                            obj["script"])
    for item in obj:
        lst.append(recursive(item, checkbox))
    return lst


menu_top = menu('Main Menu', text_main_menu, recursive(menu_items),
                checkbox=False, top_level=True)


class CascadingBoxes(urwid.WidgetPlaceholder):
    text = 'Quit - {};  '.format(exit_key) + \
           'Move through the list - up, down;  ' + \
           'Enter/Activate - enter'

    def __init__(self, box):
        super(CascadingBoxes, self).__init__(
            urwid.AttrMap(
                urwid.Filler(urwid.Text(self.text), valign='bottom'), 'bg_back'
            )
        )
        self.box_level = 0
        self.parameters = []
        self.script = ''
        self.open_box(box)

    def open_box(self, box):
        self.parameters = []
        self.script = ''
        self.original_widget = urwid.Overlay(
            urwid.AttrMap(urwid.LineBox(box), 'bg'),
            self.original_widget,
            align='center', width=('relative', 95),
            valign='top', height=('relative', 95),
        )
        self.box_level += 1
        self.script = getattr(box, 'script', '')

    def back(self):
        if self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1

    def apply_script(self):
        print("Script string: {} {}".format(self.script,
                                                ' '.join(str(val) for val in self.parameters)))

    def checkbox_changed(self, value, state):
        if state:
            self.parameters.append(value)
        else:
            try:
                self.parameters.remove(value)
            finally:
                pass

    def keypress(self, size, key):
        if key == exit_key:
            exit_program()
        return super(CascadingBoxes, self).keypress(size, key)


palette = [
    ('reversed', 'standout', ''),
    ('bg', 'bold', 'dark blue'),
    ('bg_back', 'bold', 'black'), ]

top = CascadingBoxes(menu_top)
urwid.MainLoop(top, palette=palette).run()
