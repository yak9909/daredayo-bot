import subprocess


def find(chord):
    result = subprocess.check_output(["node", "./modules/chord_finder.js", chord])
    return result.decode("utf-8").split("\n")[-2]
