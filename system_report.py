from datetime import date
import subprocess

today = date.today()
print("\033[31mSystem Report\033[0m - " + today.strftime("%B %d, %Y"))