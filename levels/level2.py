from __future__ import absolute_import, unicode_literals

from game import BaseLevel, BaseSpace

class Space(BaseSpace):
    pass


class Level(BaseLevel):
    name = 'level2'
    title = 'Outro'
    space_cls = Space