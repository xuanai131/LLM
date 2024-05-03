import subprocess

# Replace 'script.sh' with the path to your shell script
def run():
    script_path = './audio.sh'

    # Execute the shell script
    subprocess.run(['bash', script_path])