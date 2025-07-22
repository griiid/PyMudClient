from pymudclient import configs


def encode(text: str):
    try:
        return text.encode(configs.ENCODING)
    except:
        print('Encode failed', text, configs.ENCODING)
        return b''
