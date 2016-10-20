#!/usr/bin/env python
from string import Formatter
from collections import namedtuple
from pattern.en import conjugate

def objectify(dict):
    fields = ' '.join(dict.keys())
    DictTuple = namedtuple('DictTuple', fields)
    return DictTuple(**dict)

class GrammaticalString(unicode):
    def __format__(self, spec):
        #more work is needed if we want to combine grammar conversion with other formatting
        value = unicode(self)
        grammarDirective = spec
        return conjugate(value, grammarDirective)


class GrammarFormatter(Formatter):
    def convert_field(self, value, conversion):
        if 'g' == conversion:
            grammarDirective = conversion[1:]
            return GrammaticalString(value)
        else:
            return Formatter.convert_field(self, value, conversion)

    def get_value(self, key, args, kwds):
        if isinstance(key, str) or isinstance(key, unicode):
            try:
                return kwds[key]
            except KeyError:
                #allow arbitrarily named format specifications according to Pattern aliases
                return key
        else:
            print("not string key ", key)
            return Formatter.get_value(self, key, args, kwds)


grammify = GrammarFormatter().format
print(grammify('She {verb!g:{3sg}}, I {verb!g:{inf}}, it is {verb!g:{1sgp}}.', verb='sells'))
print(grammify(u'Indeed, {p.vendor} does {p.offering!g:{inf}} {p.product}', p = objectify({'product': 'iPhone', 'vendor': 'SHI', 'offering': 'SELLS'})));
