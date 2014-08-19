#!/usr/bin/kivy
__version__ = '1.0'

import kivy
import random
import math

kivy.require('1.0.6')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Point, GraphicException, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from math import sqrt

import levels


class LayoutHelper(object):
    def get_id(self, id):
        for child in self.children:
            if child.id and child.id == id:
                return child

        return None

    def get_or_create(self, id, cls, *args, **kwargs):
        item = self.get_id(id)
        if not item:
            kwargs['id'] = id
            item = cls(*args, **kwargs)
            self.add_widget(item)

        return item



class ItemWidget(Widget):
    max_opacity = 0.8

    def __init__(self, item, *args, **kwargs):
        super(ItemWidget, self).__init__(*args, **kwargs)
        self.item = item
        self.size_hint = (None, None)
        self.button = Button(
            text=item.title,
            size_hint = (None, None),
            pos=self.pos,
        )
        self.set_pos(self.item.pos)
        self.add_widget(self.button)
        self.touch_start_pos = None
        self.touch_last_pos = None
        self.speed = (0.0, 0.0)
        self.ease_interval = None
        self.fade_interval = None
        self.opacity = self.max_opacity
        self.actions = None
        self.popup = None

    def get_pos(self):
        return self.item.pos

    def set_pos(self, pos):
        self.item.pos = pos
        self.pos = list(map(int, (
            pos[0] - self.size[0] / 2,
            pos[1] - self.size[1] / 2,
        )))
        self.button.pos = self.pos

    def mod_pos(self, pos):
        pos = (
            self.get_pos()[0] + pos[0],
            self.get_pos()[1] + pos[1],
        )
        return self.set_pos(pos)

    def on_touch_down(self, touch):
        super(ItemWidget, self).on_touch_down(touch)
        if not self.collide_point(*touch.pos):
            return False

        self.touch_start_pos = touch.pos
        self.touch_last_pos = touch.pos
        self.bring_to_front()
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        self.mod_pos((
            touch.x - self.touch_last_pos[0],
            touch.y - self.touch_last_pos[1],
        ))
        self.touch_last_pos = touch.pos
        # super(self.__class__, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return

        touch.ungrab(self)

        if touch.pos == self.touch_start_pos:
            actions = self.item.get_actions()
            if actions:
                return self.show_actions()

        items = []
        for child in self.parent.children:
            if  child.collide_point(*touch.pos):
                items.append(child.item)

        if len(items) > 1:
            self.parent.react(items)

        super(ItemWidget, self).on_touch_up(touch)
        return True

    def show_actions(self):
        actions = self.item.get_actions()
        self.popup = ActionsPopup()
        self.popup.title = self.item.get_title()
        self.popup.ids.description.text = self.item.get_description()
        for action_name, method in actions:
            self.popup.ids.actions.add_widget(Button(
                text=action_name,
                on_press=self.make_action(method),
            ))
        self.popup.open()

    def make_action(self, action):
        def wrapper(instance):
            result = action()
            if not result:
                self.popup.dismiss()
                self.update_parent()

        return wrapper

    def update_parent(self):
        self.parent.update()

    def bring_to_front(self):
        parent = self.parent
        if parent.children[0] is self:
            return
        parent.remove_widget(self)
        parent.add_widget(self)

    def fadein(self):
        self.opacity = 0.0
        self.fade_interval = Clock.schedule_interval(self._fadein, 0.02)

    def _fadein(self, dt):
        self.opacity += 0.05
        if self.opacity > self.max_opacity:
            self.opacity == self.max_opacity
            self.fade_interval.cancel()
            return False

        return True

    def remove(self):
        self.parent.remove_widget(self)

    def fadeout(self):
        self.fade_interval = Clock.schedule_interval(self._fadeout, 0.02)

    def _fadeout(self, dt):
        self.opacity -= 0.05
        if self.opacity < 0:
            self.fade_interval.cancel()
            self.parent.remove_widget(self)

        return True

    def ease_random(self):
        angle_found = False
        while not angle_found:
            module = sum(self.size) / 2
            angle = random.uniform(0, 2 * math.pi)
            ease = (module * math.sin(angle), module * math.cos(angle))
            pos = self.get_pos()
            pos_future = (ease[0] + pos[0], ease[1] + pos[1])
            if self.check_pos(pos_future):
                angle_found = True
        self.ease(ease)

    def check_pos(self, pos):
        if pos[0] < self.size[0] / 2:
            return False
        if pos[1] < self.size[1] / 2:
            return False
        if pos[0] > self.parent.size[0] - self.size[0] / 2:
            return False
        if pos[1] > self.parent.size[1] - self.size[1] / 2:
            return False
        return True

    def ease(self, pos_delta):
        self.pos_delta = pos_delta
        self.ease_interval = Clock.schedule_interval(self._ease, 0.02)

    def _ease(self, dt):
        self.mod_pos(list(map(lambda x: x * 0.1, self.pos_delta)))
        self.pos_delta = list(map(lambda x: x * 0.9, self.pos_delta))

        if all([abs(i) < 0.1 for i in self.pos_delta]):
            self.pos_delta = (0.0, 0.0)
            self.ease_interval.cancel()
            return False

        return True


class MainLayout(FloatLayout):
    pass


class ActionsPopup(Popup):
    pass


class SpaceLayout(FloatLayout):
    def __init__(self, level, *args, **kwargs):
        super(SpaceLayout, self).__init__(*args, **kwargs)
        self.level = level
        self.space = level.space
        self.items = {}

    def on_touch_down(self, touch):
        result = super(SpaceLayout, self).on_touch_down(touch)
        if result:
            return True

        if self.level.on_tap(touch.x, touch.y):
            self.update()

        return False


    def update(self):
        for item in self.space.items:
            if item not in self.items:
                self.widget_add(item)


        items = list(self.items.items())

        for item, widget in items:
            if item not in self.space.items:
                self.item_remove(item)


    def react(self, items):
        products = self.space.react(items)
        self.update()
        for product in products:
            self.item_product(product)

    def item_remove(self, item):
        if item in self.space.items:
            self.space.remove(item)

        widget = self.items[item]
        widget.remove()
        del self.items[item]

    def widget_add(self, item):
        widget = ItemWidget(item)
        self.items[item] = widget
        self.add_widget(widget)
        widget.fadein()
        return widget

    def item_add(self, item_cls, pos):
        item = self.space.add(item_cls, pos)
        widget = ItemWidget(item)
        self.items[item] = widget
        self.add_widget(widget)
        widget.fadein()
        return item

    def get_widget(self, item):
        return self.items[item]

    def item_product(self, item):
        widget = self.get_widget(item)
        widget.ease_random()


class MenuScreen(Screen):
    pass


class LevelScreen(Screen, LayoutHelper):
    def __init__(self, level_cls, *args, **kwargs):
        super(LevelScreen, self).__init__(*args, **kwargs)
        self.level_cls = level_cls
        self.name = self.level_cls.name

    def on_pre_enter(self):
        space_layout = self.get_id('space')
        if space_layout is None:
            self.level = self.level_cls()
            space = self.level.get_space()
            space_layout = SpaceLayout(self.level, id='space')
            self.add_widget(space_layout)


class AlchemyApp(App):
    title = 'Alchemy'
    icon = 'icon.png'

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        for level in levels.LEVELS:
            sm.add_widget(LevelScreen(level, name=level.name))
        sm.current = 'menu'

        return sm

    def on_pause(self):
        return True

if __name__ == '__main__':
    AlchemyApp().run()
