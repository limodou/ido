option_list = (
    make_option('-t', '--test', dest='test',
        help='Test.'),
)

def call(args, options):
    print (args, options)