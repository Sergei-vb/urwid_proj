#!/usr/bin/env python3
import urwid

from get_menu_items import menu_items, exit_key


def back_button():
    button = urwid.Button('Back...')

    def back(button):
        return top.back()

    urwid.connect_signal(button, 'click', back)
    return urwid.AttrMap(button, 'bg', focus_map='reversed')


def checkbox(caption):
    item = urwid.CheckBox(caption)
    return urwid.AttrMap(item, 'bg', focus_map='reversed')


def multiple_choice_btn_group():
    button_group = [
        urwid.AttrMap(urwid.Button('Select all'), 'bg', focus_map='reversed'),
        # urwid.Button('Deselect all'),
        urwid.AttrMap(urwid.Button('Apply'), 'bg', focus_map='reversed'),
    ]
    return urwid.GridFlow(button_group, 18, 1, 1, 'center')


def check_multiple_choice(choices):
    for c in choices:
        print(c.__class__)
        if c.base_widget.__class__ == urwid.wimp.CheckBox:
            return True
    return False


def menu_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, 'bg', focus_map='reversed')


def sub_menu(caption, text, choices):
    contents = menu(caption, text, choices)

    def open_menu(button):
        return top.open_box(contents)

    return menu_button([caption, '...'], open_menu)


def menu(title, text, choices, top_level=False):
    text = '' if not text else text
    body = [urwid.Text(title), urwid.Divider(), urwid.Text(text),
            urwid.Divider()]
    body.extend(choices)

    if check_multiple_choice(choices):
        body.append(multiple_choice_btn_group())

    if not top_level:
        body.append(back_button())
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_chosen(button):
    response = urwid.Text(['You chose ', button.label, '\n'])

    def back(button):
        return top.back()

    done = menu_button('Ok', back)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def exit_program():
    raise urwid.ExitMainLoop()


def recursive(obj):
    lst = []
    if isinstance(obj, dict):
        if obj["items"] is None:
            if obj.get("checkbox", False):
                return checkbox(obj["name"])
            else:
                return menu_button(obj["name"], item_chosen)
        else:
            return sub_menu(obj["name"],
                            obj["text"],
                            recursive(obj["items"]))
    for item in obj:
        lst.append(recursive(item))
    return lst


menu_top = menu('Main Menu', 'TEXT', recursive(menu_items), top_level=True)


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
        self.open_box(box)

    def open_box(self, box):
        self.original_widget = urwid.Overlay(
            urwid.AttrMap(urwid.LineBox(box), 'bg'),
            self.original_widget,
            align='center', width=('relative', 95),
            valign='top', height=('relative', 95),
        )
        self.box_level += 1

    def back(self):
        if self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1

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
