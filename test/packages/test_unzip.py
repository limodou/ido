f = cp('pkg*', BUILD)
with cd(BUILD):
    cd(unzip(f))
    print (os.getcwd().endswith('/pkg1'))