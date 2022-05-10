import time

# 进程池进程数
CORE_NUM = 8

# 字典
VALUE="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ%&^@_.-!{}"

# banner
BANNER = """\033[01;31m\
              ___.    __                .__   
__  _  __ ____\_ |___/  |_  ____   ____ |  |  
\ \/ \/ // __ \| __ \   __\/  _ \ /  _ \|  |  
 \     /\  ___/| \_\ \  | (  <_> |  <_> )  |__
  \/\_/  \___  >___  /__|  \____/ \____/|____/
             \/    \/    
\033[01;37m[*]time : {0}
""".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))