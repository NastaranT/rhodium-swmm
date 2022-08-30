import weakref
from pkg_resources import set_extraction_path
from pathlib import Path

from rhodium import model
from . import swmm_input_element

class RhodiumParameter(swmm_input_element.SwmmInputElement):

    _instances = set()

    def __init__(self, value, default=None) -> None:
        self.default = default
        if isinstance(value, (model.Uncertainty, model.Lever)):
            self.rhodium_model_param = value
            self.value = default
        else:
            self.value = value
            self.rhodium_model_param = None

        self._saved_value = self.value

        self.__class__._instances.add(weakref.ref(self))

    def save_value(self):
        self._saved_value = self.value

    def restore_value(self):
        self.value = self._saved_value

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)

        cls._instances -= dead

    @classmethod
    def save_all_values(cls):
        for param in cls.getinstances():
            param.save_value()

    @classmethod
    def restore_all_values(cls):
        for param in cls.getinstances():
            param.restore_value()

    @classmethod
    def get_rhodium_levers(cls):
        levers = {}
        for obj in cls.getinstances():
            if isinstance(obj.rhodium_model_param, model.Lever):
                levers[obj.rhodium_model_param.name] = obj.rhodium_model_param
        return levers

    @classmethod
    def get_rhodium_uncertainties(cls):
        uncertainties = {}
        for obj in cls.getinstances():
            if isinstance(obj.rhodium_model_param, model.Uncertainty):
                uncertainties[obj.rhodium_model_param.name] = obj.rhodium_model_param
        return uncertainties

    @classmethod
    def get_rhodium_parameters(cls):
        params = {}
        for obj in cls.getinstances():
            if isinstance(obj.rhodium_model_param, (model.Lever, model.Uncertainty)):
                params[obj.rhodium_model_param.name] = model.Parameter(obj.rhodium_model_param.name, default_value=obj.default)

        return params

    @classmethod
    def get_levers_and_uncertainties(cls):
        params = {}
        for obj in cls.getinstances():
            if isinstance(obj.rhodium_model_param, (model.Uncertainty, model.Lever)):
                if obj.rhodium_model_param.name in params:
                    params[obj.rhodium_model_param.name].append(obj)
                else:
                    params[obj.rhodium_model_param.name] = [obj]
        return params
        

    def __str__(self) -> str:
        return str(self.value)

    def __complex__(self):
        return self.value.__complex__()

    def __int__(self):
        return int(self.value)

    def __long__(self):
        return self.value.__long__()

    def __float__(self):
        return float(self.value)

    def __oct__(self):
        return self.value.__oct__()

    def __hex__(self):
        return self.value.__hex__()

    def __add__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value + other

    def __radd__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other + self.value

    def __sub__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value - other

    def __rsub__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other - self.value

    def __mul__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value * other

    def __rmul__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other * self.value

    def __div__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value / other

    def __rdiv__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other / self.value

    def __mod__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value % other

    def __rmod__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other % self.value

    def __pow__(self, other, modulo = None):
        if isinstance(other, RhodiumParameter):
            other = other.value
        power = (self.value ** other)
        if modulo is not None:
            power = power % modulo
        return power

    def __rpow__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other ** self.value

    def __lshift__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value << other

    def __rlshift__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other << self.value

    def __rshift__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value >> other

    def __rrshift__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other >> self.value

    def __and__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value & other

    def __rand__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other & self.value

    def __xor__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value ^ other

    def __rxor__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other ^ self.value

    def __or__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value | other

    def __ror__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return other | self.value
        
    def __neg__(self):
        return self.value.__neg__()

    def __pos__(self):
        return self.value.__pos__()

    def __abs__(self):
        return self.value.__abs__()

    def __coerce__(self, other):
        if isinstance(other, RhodiumParameter):
            other = other.value
        return self.value.__coerce__(other)


class DictionaryRhodiumParameter(RhodiumParameter):
    def __init__(self, value, value_map, default=None):
        self.value_map = value_map
        super(DictionaryRhodiumParameter, self).__init__(value, default=default)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = self.value_map.get(v)
        if self._value is None:
            self._value = v

        #if isinstance(self._value, list):
            #self._value = self.value_map.random.choice(v)

class SwmmPathParameter(DictionaryRhodiumParameter):
    def __init__(self, value, value_map, default):
        for (key, v) in value_map.items():
            value_map[key] = "\"{}\"".format(v)
        super().__init__(value, value_map, default=default)
