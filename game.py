class Item(object):
    title = 'Item'
    desc = 'Simple description'
    source_clss = ()

    def __init__(self, space, pos):
        self.space = space
        self.pos = list(map(float, pos))

    def remove(self):
        self.space.remove(self)

    def get_title(self):
        return self.title

    def get_description(self):
        return self.desc

    def get_actions(self):
        result = []
        for method_name in dir(self):
            if method_name.startswith('action'):
                result.append((method_name.split('_', 1)[-1], getattr(self, method_name)))

        return result

    def has_actions(self):
        for method_name in dir(self):
            if method_name.startswith('action_'):
                return True

        return False

    def do_action(self, action_name):
        return getattr(self, 'action_' + action_name)()


class BaseLevel(object):
    def __init__(self):
        self.space = None

    def get_space(self):
        if not self.space:
            self.space = self.space_cls()

        return self.space

    def on_tap(self, x, y):
        return


class BaseReactor(object):
    items_clss = []

    def __init__(self):
        self.reactions = []
        if self.items_clss:
            for item_cls in self.items_clss:
                for sources in item_cls.source_clss:
                    self.reactions.append((sources, (), (item_cls, )))

    @staticmethod
    def compare_items(items, sources_sample):
        for i, item in enumerate(items):
            if i >= len(sources_sample):
                return True

            if item.__class__ != sources_sample[i]:
                return False

        return True

    def react(self, items):
        for sources, remains, products in self.reactions:
            if self.compare_items(items, sources):
                non_react = items[len(sources):]

                remains = list(remains)
                for item in items[:len(sources)]:
                    if item.__class__ in remains:
                        non_react.append(item)
                        remains.remove(item.__class__)

                return non_react, products


class BaseSpace(object):
    title = 'Default'
    reactor_cls = BaseReactor

    def __init__(self):
        self.items = []
        self.reactor = self.reactor_cls()

    def add(self, item_cls, pos):
        item = item_cls(self, pos)
        self.items.append(item)
        return item

    def react(self, items):
        item = items[0]
        result = self.reactor.react(items)
        if not result:
            return []

        items_remain, products_clss = result
        products = []
        for product_cls in products_clss:
            products.append(self.add(product_cls, item.pos))
        for item in items:
            if item not in items_remain:
                self.remove(item)

        return products

    def move(self, item, speed):
        pass

    def remove(self, item):
        self.items.remove(item)