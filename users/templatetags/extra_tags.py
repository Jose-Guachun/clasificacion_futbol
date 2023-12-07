from django import template

register = template.Library()

def callmethod(obj, methodname):
    method = getattr(obj, methodname)
    if "__callArg" in obj.__dict__:
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()

def args(obj, arg):
    if "__callArg" not in obj.__dict__:
        obj.__callArg = []
    obj.__callArg.append(arg)
    return obj

def encrypt(value):
    if value == None:
       return value
    myencrip = ""
    if type(value) != str:
        value = str(value)
    i = 1
    for c in value.zfill(20):
        myencrip = myencrip + chr(int(44450/350) - ord(c) + int(i/int(9800/4900)))
        i = i + 1
    return myencrip

def title_cap(texto=''):
    return " ".join([x.capitalize() if x.__len__() > 3 else x.lower() for x in f"{texto}".lower().split(' ')])


register.filter("title_cap", title_cap)
register.filter("encrypt", encrypt)
register.filter("args", args)
register.filter("call", callmethod)