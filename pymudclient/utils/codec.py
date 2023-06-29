CODEC = 'big5hkscs'


def enc(text):
    try:
        return text.encode(CODEC)
    except:
        print('Encode failed')
        return ''

def dec(text):
    return text.decode(CODEC, 'ignore')
