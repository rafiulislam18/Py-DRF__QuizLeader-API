from django.core.management.utils import get_random_secret_key

def generate_key():
    return get_random_secret_key()

if __name__ == "__main__":
    print(generate_key())
