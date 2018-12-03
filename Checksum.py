import binascii


def validate_checksum(message):
    try:
        msg,reported_checksum = message.rsplit('|',1)
        msg += '|'
        return generate_checksum(msg) == reported_checksum
    except:
        return False

def generate_checksum(message):
    return str(binascii.crc32(message) & 0xffffffff)
