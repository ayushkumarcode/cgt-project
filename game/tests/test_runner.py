"""Runs inside Docker. Tests leaders against real engine."""
import gc, numpy as np

class Leader:
    _subclass_registry = {}
    def __init__(self, name, engine):
        self.name = name; self.engine = engine
    @classmethod
    def cleanup_old_subclasses(cls):
        for sub in list(cls.__subclasses__()):
            if sub.__name__ in cls._subclass_registry:
                del cls._subclass_registry[sub.__name__]
        gc.collect()
    @classmethod
    def update_subclass_registry(cls):
        cls.cleanup_old_subclasses()
        cls._subclass_registry = {s.__name__: s for s in cls.__subclasses__()}
    def new_price(self, date): pass
    def get_price_from_date(self, date):
        return self.engine.exposed_get_price(date)
