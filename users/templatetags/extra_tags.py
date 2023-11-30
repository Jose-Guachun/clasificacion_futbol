from django import template

register = template.Library()

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
register.filter("encrypt", encrypt)