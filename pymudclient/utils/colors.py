_COLOR_REPLACE_MAP = [
    ('$NOR$', '\x1B[m'),
    ('$BLK$', '\x1B[30m'),
    ('$RED$', '\x1B[31m'),
    ('$GRN$', '\x1B[32m'),
    ('$YEL$', '\x1B[33m'),
    ('$BLU$', '\x1B[34m'),
    ('$MAG$', '\x1B[35m'),
    ('$CYN$', '\x1B[36m'),
    ('$WHT$', '\x1B[37m'),
    ('$HIR$', '\x1B[1;31m'),
    ('$HIG$', '\x1B[1;32m'),
    ('$HIY$', '\x1B[1;33m'),
    ('$HIB$', '\x1B[1;34m'),
    ('$HIM$', '\x1B[1;35m'),
    ('$HIC$', '\x1B[1;36m'),
    ('$HIW$', '\x1B[1;37m'),
]


def color_convert(text):
    for old, new in _COLOR_REPLACE_MAP:
        text = text.replace(old, new)
    return text
