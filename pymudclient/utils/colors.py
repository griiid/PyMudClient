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


# TODO: 整理這個 function
def remove_strange_color_code(content):
    '''移除中文字 2 個 byte 中間會被插入的 \x1B[1m (會導致中文字變亂碼)'''
    new_content = bytearray()

    status = 0
    for i in range(len(content)):
        if status == 0:
            new_content.append(content[i])
            # Big5 的範圍才要處理
            if content[i] >= 0x81 and content[i] <= 0xFE:
                status = 1

        elif status == 1:
            if i+3 < len(content) and \
                    content[i] == 0x1B and \
                    content[i+1] == ord('[') and \
                    content[i+2] == ord('1') and \
                    content[i+3] == ord('m'):
                status = 2
                skip = 3
            else:
                new_content.append(content[i])
                status = 0

        elif status == 2:
            skip -= 1
            if skip == 0:
                status = 0

    return new_content

