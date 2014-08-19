from __future__ import absolute_import, unicode_literals

from game import BaseLevel, BaseSpace, Item

class Space(BaseSpace):
    pass


class Level(BaseLevel):
    name = 'level1'
    title = 'Intro'
    space_cls = Space

    def on_tap(self, x, y):
        self.space.add(Item, (x, y))
        return True