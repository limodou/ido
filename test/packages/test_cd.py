def call(args, options):
    d = os.getcwd()
    with cd('/usr'):
        print (os.getcwd() == '/usr')
    print (d == os.getcwd())