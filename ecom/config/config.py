import os
import environ


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, 'config/config.env'))


SECRET_KEY = env.str('SECRET_KEY', default="")

EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')

STRIPE_PUB_KEY = env.str('STRIPE_PUB_KEY', default='')
STRIPE_API_KEY = env.str('STRIPE_API_KEY', default='')
