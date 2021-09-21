from django.template.defaulttags import register

@register.filter

def interval( value, arg ):
  try:

    #interval=value-arg
    #return interval.seconds
    interval = value-arg
    a = "esdf %d" % interval.hours
    return a

  except: pass

  return ''

