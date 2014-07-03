redis = cp('redis*', BUILD, wget='http://download.redis.io/releases/redis-2.8.11.tar.gz')
cd(BUILD)
cd(tarx(redis))
sh('make install PREFIX=%s' % PREFIX)
