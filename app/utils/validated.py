import string


class Validadores:
    def __init__(self):
        self.min_length = 8

    def password(self, senha):
        if len(senha) < self.min_length: return False
        tem_maiuscula = any(c.isupper() for c in senha)
        tem_minuscula = any(c.islower() for c in senha)  
        tem_numero    = any(c.isdigit() for c in senha) 
        tem_especial  = any(c in string.punctuation for c in senha)
        return tem_maiuscula and tem_minuscula and tem_numero and tem_especial
