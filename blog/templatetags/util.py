from django.template.defaulttags import register

@register.filter

def less( value, arg ):
  try:

    #interval=value-arg
    #return interval.seconds
    return value<arg
    
  except: pass

  return ''

