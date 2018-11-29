### python爬虫

环境要求：python3，mysql 5.7

使用组件库：requests，toradb兼容python3版

配置好数据库和初始用户，执行 `python crawler.py`即可



爬取数据原理：利用game.weixin.qq.com接口，抓取用户和对战数据，通过比赛详情接口，获取用户opend_id，进而实现递归遍历。

目前微信对战用户关系并不完全对用户开放，数据局限性非常大，无解~



附接口汇总：

##### 1.获取英雄详情：

​     url：https://game.weixin.qq.com/cgi-bin/gamewap/gamemoba
​    方法：GET
​    参数： uin、key、pass_ticket

##### 2.获取用户详情：

​    url: https://game.weixin.qq.com/cgi-bin/gamewap/getusermobagameindex
​    方法：GET
​    参数：uin、key、pass_ticket、 openid

##### 3.获取用户英雄池：

​    url: https://game.weixin.qq.com/cgi-bin/gamewap/getmobauserheroinfo
​    方法：GET
​    参数：uin、key、pass_ticket、zone_area_id、 openid

##### 4.获取比赛列表：

​    url: https://game.weixin.qq.com/cgi-bin/gamewap/getusermobabattleinfolist
​    方法：GET
​    参数：uin、key、pass_ticket、offset、limit、 openid 、zone_area_id

##### 5.获取比赛详情：

​    url: https://game.weixin.qq.com/cgi-bin/gamewap/getsmobabattledetail
​    方法：GET
​    参数：game_svr_entity、game_seq、relay_svr_entity、 openid