filename = cp('a*', BUILD)
cd(BUILD)
sh('tar xvfz %s' % filename)