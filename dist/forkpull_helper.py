import os
from subprocess import call, check_output

with open('repos.txt') as f:
	for repo in f.readlines():
		CMD = ['forkpull.exe']
		CMD.append(repo)
		call(CMD)