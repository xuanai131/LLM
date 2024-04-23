import subprocess

# Replace 'script.sh' with the path to your shell script
def run():
    script_path = '/var/www/html/flask/audio.sh'

    # Execute the shell script
    subprocess.run(['bash', script_path])