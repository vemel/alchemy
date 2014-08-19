from __future__ import absolute_import, unicode_literals

import random

from game import BaseLevel, BaseSpace, Item, BaseReactor


class Item(Item):
    title = 'New item'

    def action_dublicate(self):
        self.space.add(self.__class__, self.pos)


class Item2(Item):
    title = 'Another item'
    source_clss = (
        (Item, Item),
    )


class Item3(Item):
    title = 'Transmute me!'

    def action_transmute(self):
        self.space.add(Item, self.pos)
        self.remove()


class Reactor(BaseReactor):
    items_clss = [Item, Item2, Item3]


class Space(BaseSpace):
    reactor_cls = Reactor


class Level(BaseLevel):
    name = 'level1'
    title = 'Intro'
    space_cls = Space

    def on_tap(self, x, y):
        self.space.add(random.choice([Item, Item2, Item3]), (x, y))
        return True