#!/usr/bin/env python3

# This is a driver for the CS324 Bandit Homework. It runs all of the tests automatically from your file bandit.txt

# You MUST do this part from BYU's campus network.

# To run
# ./SshTester.py bandit.txt
# Do not turn this file in 
# 
# Troubleshooting 
#   Permission Denied - make sure SshTester.py has execute permission, you can run "chmod +x SshTester.py" to possibly fix
#   Formatting error - Some small thing in your bandit.txt doesn't match the arbitrary way we've decided to parse. The line number is normaly right, not always.
#   

from pexpect import pxssh, spawn
import sys
import os

POINTS_PER_LEVEL = 2
NUM_LEVELS = 10

class BanditLevel:
    def __init__(self, level = 0, pwd = "0", cmd = "0"):
        self.level = level
        self.pwd = pwd
        self.cmd = cmd

    def __str__(self):
        return self.level + '\n' + self.pwd + '\n' + self.cmd


class Student:
    def __init__(self, submission_file):
        self.submission_file = submission_file
        self.responses = []
        
    def extract_responses(self):
        f = open(self.submission_file, 'r')
        line_num = 0
        while True:
            line = f.readline()
            line_num += 1
            if not line:
                break
            if line.find("evel") != -1 or line.find("EVEL") != -1:
                level = line.strip()
                try:
                    level_num = int(level[5:-1])
                except ValueError as e:
                    print(f'Line {line_num}: Formatting error "{level}"')
                    print('Make sure your commands and passwords are on one line each and you have \na ":" after the level number\n')
                    continue
                    # exit(-1)
                pwd = f.readline().strip()
                cmd = Student.remove_prompt(f.readline()).strip()
                self.responses.append(BanditLevel(level_num, pwd, cmd))
                line_num += 2
        
    def grade(self):
        score = 0
        total = NUM_LEVELS * POINTS_PER_LEVEL
        
        hostname = "imaal.byu.edu"

        c = pxssh.pxssh(echo=False)
        c.force_password = True
        c.login(hostname, username='bandit0', password='bandit0')
        # Recent versions of libreadline enable bracketed-paste mode by
        # default, which causes issues for pexpect when wrapping a
        # readline-enabled command (like bash or python).  So we disable
        # bracketed paste explicitly here.
        # See https://github.com/pexpect/pexpect/issues/669
        c.sendline("bind 'set enable-bracketed-paste off'")

        for test in self.responses:

            if test.level >= NUM_LEVELS:
                continue

            print(f'Level {test.level + 1} (from Level {test.level}):')
            try:
                if test.level == NUM_LEVELS:
                    pass
                else: 
                    user_name = 'bandit' + str(test.level+1)
                    nl = pxssh.pxssh(echo=False)
                    nl.force_password = True
                    nl.login(hostname, username=user_name, password=test.pwd)
                    # see note above...
                    nl.sendline("bind 'set enable-bracketed-paste off'")
                print(f'\tPassword Check: Passed')
                score += 1

                if test.level == 7:
                    pass
                else:
                    if test.cmd.find(";") != -1 or test.cmd.find("&&") != -1:
                        raise Exception('Pipeline must be a one-liner (may not have ; or &&)')
                    try:
                        c.prompt()
                        c.sendline(test.cmd)
                        c.prompt()
                        output = (c.before).decode('utf-8').strip()
                    except Exception as e:
                        raise Exception(f'No way to check because your previous password check failed')
                    else:
                        if output != test.pwd:
                            raise Exception(f'\nYour password was\n\t{test.pwd}\nYour command returned\n\t{output}')
                    
                print(f'\tPipeline Check: Passed')
                score += 1

            except pxssh.ExceptionPxssh as e:
                print(f'\tPassword Check: Failed to login to the next level due to {e}')
                print(f'\tPipeline Check: Not tested due to password check failing')
            except pxssh.TIMEOUT as e:
                print(f'\tLogin TIMEOUT.')
            except Exception as e:
                print(f'\tPipeline Check: Failed - {e}')
            else:
                # score += POINTS_PER_LEVEL
                pass
            finally:
                try:
                    c.logout()
                except:
                    # This exception is swallowed here, but will only happen when the exception that says 
                    # 'No way to check because your previous password check failed' is called
                    pass
                c=nl
                nl = 0
        print(f'Score: {score}/{total}')

    def remove_prompt(line):
        if line.find("@imaal") != -1:
            return line[line.find("~$")+2::]
        return line

def usage():
    print('Usage: ./SshTester.py <file_name>')

def main():
    if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
        usage()
        exit(-1)
    file = sys.argv[1]
    try:
        s = Student(file)
        s.extract_responses()
        s.grade()
    except Exception as err:
        print(f'Unknown problem. Here is the error\n{err}\nGood luck!')
       
if __name__ == '__main__':
    main()
