import subprocess

def runcmd(cmd):
    print(" ".join(cmd))
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print(f"FAILED: {exc.returncode}")
        output = exc.output
    print(output.decode("utf-8"))
