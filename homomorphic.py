import random
import gmpy2

class Paillier:
    def __init__(self, key_size=512):
        self.key_size = key_size
        self.public_key, self.private_key = self.generate_keys()

    def generate_keys(self):
        p = gmpy2.next_prime(random.getrandbits(self.key_size))
        q = gmpy2.next_prime(random.getrandbits(self.key_size))
        n = p * q
        λ = (p - 1) * (q - 1) // gmpy2.gcd(p - 1, q - 1)
        g = n + 1
        μ = gmpy2.invert(λ, n)
        return (n, g), (λ, μ, n)

    def encrypt(self, m, public_key):
        n, g = public_key
        r = random.randint(1, n - 1)
        return (pow(g, m, n * n) * pow(r, n, n * n)) % (n * n)


    def decrypt(self, c, private_key):
        λ, μ, n = private_key
        x = pow(c, λ, n * n) - 1
        return int((x // n) * μ % n)

    def homomorphic_addition(self, a, b, public_key):
        """input: a, b : returns a + b"""
        return (a * b) % (public_key[0] ** 2)

    def homomorphic_subtraction(self, a, b, public_key):
        """input: a, b : returns a - b"""
        n, _ = public_key
        b_inv = gmpy2.invert(b, n * n)  # modular inverse of Enc(b)
        return (a * b_inv) % (n * n)  # Enc(a) * Enc(b)^(-1) mod n²

    
if __name__ == "__main__":
    p = Paillier()
    pb, pr = p.generate_keys()
    a = p.encrypt(10, pb)
    b = p.encrypt(5, pb)

    print(p.decrypt(p.homomorphic_addition(a, b, pb), pr))
    print(p.decrypt(p.homomorphic_subtraction(a, b, pb), pr))