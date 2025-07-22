from pymudclient.configs import ENCODING


def enc(text):
    try:
        return text.encode(ENCODING)
    except:
        print('Encode failed')
        return ''


def dec(text):
    return text.decode(ENCODING, 'ignore')
