import os, time

# periodically checkes for new additions
def check_new_additions():
    while True:
        if os.path.exists('new_additions.csv'):
            with open('new_additions.csv', 'r') as rf:
                with open("mvStatus_server.csv", 'a') as wf:
                    for line in rf:
                        wf.write(line)
            os.system('rm new_additions.csv')
        else:
            time.sleep(10)

if __name__ == '__main__':
    check_new_additions()