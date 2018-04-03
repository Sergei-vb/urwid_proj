#!/usr/bin/env python3
import urwid

import get_menu_items

main_menu = get_menu_items.menu_items
exit_key = get_menu_items.exit_key


def back_button():
    button = urwid.Button('Back...')

    def back(button):
        return top.back()

    urwid.connect_signal(button, 'click', back)
    return urwid.AttrMap(button, 'bg', focus_map='reversed')


def menu_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, 'bg', focus_map='reversed')


def sub_menu(caption, text, choices):
    contents = menu(caption, text, choices)

    def open_menu(button):
        return top.open_box(contents)

    return menu_button([caption, '...'], open_menu)


def menu(title, text, choices):
    body = [urwid.Text(title), urwid.Divider(), urwid.Text(text),
            urwid.Divider()]
    body.extend(choices)
    body.append(back_button())
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_chosen(button):
    response = urwid.Text(['You chose ', button.label, '\n'])
    done = menu_button('Ok', run_script)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def run_script(button):
    pass


def exit_program():
    raise urwid.ExitMainLoop()


def recursive(obj):
    lst = []
    if isinstance(obj, dict):
        if obj["items"] is None:
            return menu_button(obj["name"], item_chosen)
        else:
            return sub_menu(obj["name"], obj["text"], recursive(obj["items"]))
    for item in obj:
        lst.append(recursive(item))
    return lst


menu_top = menu('Main Menu', 'MAIN TEXT', recursive(main_menu))


class CascadingBoxes(urwid.WidgetPlaceholder):
    text = 'Quit - {};  '.format(exit_key) + \
           'Move through the list - up, down;  ' + \
           'Enter/Activate - enter'

    def __init__(self, box):
        super(CascadingBoxes, self).__init__(
            urwid.AttrMap(
                urwid.Filler(urwid.Text(self.text), valign='bottom'), 'bg'
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
            min_width=24, min_height=8, )
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
    ('bg', 'bold', 'dark blue'), ]

top = CascadingBoxes(menu_top)
urwid.MainLoop(top, palette=palette).run()
