try:
    buff = ''
    while True:
        input = sys.stdin.read(1)
        if len(input) > 0:
            buff += input
            if len(buff) >= 4:
                if buff[0] != address:
                    buff = ''
                else:
                    result = processMessage(buff)
                    if result != None:
                        sys.stdout.write(result)
                        sys.stdout.flush()
                        # sys.stderr.write("hello")
                        # sys.stderr.flush()
                    buff = ''

except KeyboardInterrupt:
    sys.stdout.flush()
    pass
