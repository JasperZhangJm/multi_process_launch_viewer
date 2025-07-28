# multi_process_launch_viewer
python实现分布式并发启动多台ec2上的shell脚本

1、main.py 文件中的代码是用python代码代替shell启动master/viewer的代码，没有调试完成；<br>
2、multi_bind.py 文件中的代码是将开发提供的100个sn绑定到我的账号下，用于获取viewer端的ak、sk、token临时凭证，ak，sk，token是分权限的，即master权限、viewer权限；
3、sn_channel_list.txt 这里面的sn和channel是提供给shell启动脚本使用的，需要放在ec2实例上，如果有多台ec2实例，需要放多份；
4、test4fabric.py 使用fabric ssh 连接到ec2
5、test4paramiko.py 使用paramiko ssh 连接到ec2
