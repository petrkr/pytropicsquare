from tropicsquare.ports.micropython.aesgcm import AESGCM

def main():
    gcm = AESGCM(b'\x00'*32)

    print(gcm.encrypt(b'\x00' * 12, b"Test from uPy", b''))
    
    enc = bytes.fromhex("8fcf2f576d090207c7257ba1320a3f95a0b7958317b1f61a")    
    print(gcm.decrypt(b'\x00' * 12, enc , b''))


if __name__ == "__main__":
    main()
