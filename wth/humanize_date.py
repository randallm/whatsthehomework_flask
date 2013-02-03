# Modified version of http://stackoverflow.com/a/5164027/898247

from math import fabs
import datetime

def humanize_date(date):
    difference = datetime.datetime.utcnow() - date
    s_difference = difference.seconds

    if difference.days > 7:
        return date.strftime('%m/%d/%y')
    elif difference.days == 1:
        return 'Yesterday'
    elif difference.days > 1:
        return '%i days ago' % (difference.days)
    elif difference.days == -1:
        return 'Tomorrow'
    elif difference.days < 0:
        return 'In %i days' % (int(fabs(difference.days)))

    elif s_difference < 120:
        return 'Just now'
    elif s_difference < 7200:
        return '1 hour ago'
    else:
        return '%i hours ago' % (s_difference/3600)