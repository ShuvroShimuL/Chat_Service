import subprocess

cmd = "streamlit run page.py"

if __name__ == "__main__":
    p = subprocess.Popen(cmd, shell = True)
