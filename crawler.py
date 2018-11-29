#!/usr/bin/env python
# -*- coding' : 'utf-8 -*-
from queue import Queue
import time
import torndb
from logger import logger
from WzFetcher import Fetcher


db_cfg = {'host': 'xx.xx.xx.xx',
          'port': 'xxxx',
          'database': 'study_crawler',
          'user': 'xxx',
          'password': 'xxxxxx'}
db = torndb.Connection(host="%s:%s" % (db_cfg['host'], db_cfg['port']), database=db_cfg['database'],
                       user=db_cfg['user'], password=db_cfg['password'], charset='utf8mb4')

origin_user = {
    'open_id': 'xxxxxxxxxxxxxxx',
    'zone_area_id': 4051
}


fetch = Fetcher(key='beffa4e39c973612ae71da8b7baac956430d5db8dbb2a04b25a8977752b4d9903b913450a0252d0152fad0ddcb80874f29a7c0fb75b226e57ef6e67d204a381a75649c583fa482e1cae73b0ff4fe7619',
                zone_area_id= origin_user['zone_area_id'],
                openid= origin_user['open_id'],
                ticket='xxxxxxxxxxxx')

class MyExpection(Exception):
    def __init__(self,msg):
        self.message = msg

def init_hero_list():
    res = fetch.get_hero_list()
    print(res)
    if res is not None and res['errcode'] is not None and res['errcode'] == 0:
        category_list = res['moba']['category_list']
        sql = 'insert IGNORE into hero (hero_id, game_hero_id, icon, brief_name, category, category_id) values (%s, %s, %s, %s, %s, %s)'
        for category in category_list:
            hero_list = [(hero['hero_id'], hero['game_hero_id'], hero['icon'], hero['brief_name'], hero['category'],
                          hero['category_id']) for hero in category['hero_item_list']]
            db.executemany(sql, hero_list)
    else:
        raise Exception("error %s" % res['errcode'])


def init_user():
    res = fetch.get_user_info()
    logger.info(res)

    if res is not None and res['errcode'] is not None and res['errcode'] == 0:
        u = res['user_info']
        if len(db.query("select id from user where open_id='%s' and zone_area_id=%s" % (u.get('open_id') , u.get('zone_area_id')))) == 0:
            sql = "insert ignore INTO `user` (`open_id`, `zone_area_id`, `nick_name`, `head_img_url`, `game_name`, `service_name`, " \
                  "`rank_desc`, `winning_percentage`, `rank_lift`, `win_desc`, `rank_star`, `ladder_score`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            user_dic = (u.get('open_id'), u.get('zone_area_id'), u.get('nick_name'), u.get('head_img_url'), u.get('game_name'),
                        u.get('service_name'), u.get('rank_desc'), u.get('winning_percentage'), u.get('rank_lift'),
                        u.get('win_desc'), u.get('rank_star'), u.get('ladder_score')
                        )
        else:
            sql = "update `user` set `nick_name`=%s, `head_img_url`=%s, `game_name`=%s, `service_name`=%s, `rank_desc`=%s, " \
                  "`winning_percentage`=%s, `rank_lift`=%s, `win_desc`=%s, `rank_star`=%s, `ladder_score`=%s " \
                  "where `open_id`=%s and `zone_area_id`=%s"
            user_dic = (u.get('nick_name'), u.get('head_img_url'), u.get('game_name'),
                        u.get('service_name'), u.get('rank_desc'), u.get('winning_percentage'), u.get('rank_lift'),
                        u.get('win_desc'), u.get('rank_star'), u.get('ladder_score'), u.get('open_id'), u.get('zone_area_id')
                        )
        db.executemany(sql, [user_dic])
    else:
        raise Exception("error %s" % res['errcode'])


def init_user_hero_info():
    res = fetch.get_user_hero_info()
    if res is not None and res['errcode'] is not None and res['errcode'] == 0:
        user_hero_list = res['hero_info']['user_hero_list']
        sql = "INSERT IGNORE INTO `user_hero` (`hero_id`, `open_id`, `zone_area_id`, `hero_name`, `combat_power`, `winning_percentage`, `pro_level`, " \
              "`category`, `battle_cnt`, `total_win_rate`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        data_list = [(hero['hero_id'], fetch.get_working_open_id(), fetch.get_working_zone_area_id(), hero.get('hero_name'),
                      hero.get('combat_power'), hero.get('winning_percentage'), hero.get('pro_level'),
                      hero.get('category'), hero.get('battle_cnt'), hero.get('total_win_rate')) for hero in user_hero_list]
        db.executemany(sql, data_list)
    else:
        raise Exception("error %s" % res)


def init_battle_info_list():
    res = fetch.get_battle_info_list()
    if res is not None and res['errcode'] is not None and res['errcode'] == 0:
        battle_list = res['battle_info']['battle_list']
        sql = "INSERT IGNORE INTO `battle` (`game_seq`, `game_type`, `game_svr_entity`, `relay_svr_entity`, `dt_event_time`) VALUES (%s, %s, %s, %s, %s);"
        data_list = [(battle['game_seq'], battle['game_type'], battle['game_svr_entity'], battle['relay_svr_entity'],
                      battle['dt_event_time']) for battle in battle_list]
        db.executemany(sql, data_list)

        user_list = []
        for battle in battle_list:
            user_list += init_battle_detail(battle['game_seq'], battle['game_svr_entity'], battle['relay_svr_entity'])
            time.sleep(0.5)
        return user_list
    else:
        raise Exception("error %s" % res)


def init_battle_info_list_all():
    i = 0
    the_end = False
    user_list = []
    while not the_end:
        res = fetch.get_battle_info_list(offset=i*10)
        time.sleep(1)
        logger.info("处理战绩，页数 %s" % i)
        i += 1

        if res is not None and res['errcode'] is not None and res['errcode'] == 0:
            battle_list = res.get('battle_info').get('battle_list')
            if not battle_list or len(battle_list) == 0:
                break
            sql = "INSERT IGNORE INTO `battle` (`game_seq`, `game_type`, `game_svr_entity`, `relay_svr_entity`, `dt_event_time`) VALUES (%s, %s, %s, %s, %s);"
            data_list = [(battle['game_seq'], battle['game_type'], battle['game_svr_entity'], battle['relay_svr_entity'],
                          battle['dt_event_time']) for battle in battle_list]
            db.executemany(sql, data_list)

            for battle in battle_list:
                db_battle_list = get_battle_info(battle['game_seq'], battle['game_svr_entity'], battle['relay_svr_entity'])
                if db_battle_list and len(db_battle_list) > 0:
                    logger.info("数据库已存在对战详情: %s, %s, %s" % (battle['game_seq'], battle['game_svr_entity'], battle['relay_svr_entity']))
                    continue
                try:
                    user_list += init_battle_detail(battle['game_seq'], battle['game_svr_entity'], battle['relay_svr_entity'])
                    time.sleep(1)
                except MyExpection as me:
                    print(me)
                    the_end = True
                    break
        else:
            raise Exception("error %s" % res)
    return user_list


def init_battle_detail(game_seq, game_svr_entity, relay_svr_entity):
    res = fetch.get_battle_info_detail(game_seq, game_svr_entity, relay_svr_entity)
    logger.info("写入对战详情数据：%s, %s, %s" % (game_seq, game_svr_entity, relay_svr_entity) )
    if res is not None and res['errcode'] is not None and res['errcode'] == 0:
        battle_detail = res.get('normal_battle_detail')
        if not battle_detail:
            logger.error(res)
            raise MyExpection("对战详情不存在")

        sql = "update battle set blue_kill_cnt=%s, red_kill_cnt=%s, is_blue=%s, game_time=%s, is_victory=%s where " \
              "game_seq=%s and game_svr_entity=%s and relay_svr_entity=%s"
        data_list = [(battle_detail['blue_kill_cnt'], battle_detail['red_kill_cnt'], battle_detail['is_blue'],
                      battle_detail['game_time'], battle_detail['is_victory'], game_seq, game_svr_entity, relay_svr_entity)]
        db.executemany(sql, data_list)

        user_battle_detail_list = battle_detail['user_battle_detail']
        insert_sql = "INSERT IGNORE INTO `user_battle_detail` (`open_id`, `name`, `game_name`, `hero_id`, `game_seq`, `game_svr_entity`, `relay_svr_entity`, " \
                     "`game_type`, `hero_name`, `total_hurt`, `total_hurt_hero`, `suffer_hurt`, `total_hurt_percent`, `total_hurt_hero_percent`, " \
                     "`suffer_hurt_percent`, `kill_cnt`, `dead_cnt`, `assist_cnt`, `is_blue`, `grade_of_rank`, `lose_mvp`, `is_mvp`, " \
                     "`pvp_level`, `total_in_battle_coin`, `used_time`, `mvp_score_tth`, `zone_area_id`, `is_low_score`, `is_victory`, `acnt_camp`, " \
                     "`is_five_army`, `game_result`, `six_kill`, `seven_kill`, `eight_kill`, `game_score`, `multi_camp_rank`, `is_ai_pvp`) VALUES " \
                     "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        detail_list = [(d.get('open_id'), d.get('name'), d.get('game_name'), d.get('hero_id'), game_seq, game_svr_entity, relay_svr_entity,
                        battle_detail.get('game_type'), d.get('hero_name'), d.get('total_hurt'), d.get('total_hurt_hero'), d.get('suffer_hurt'),
                        d.get('total_hurt_percent'), d.get('total_hurt_hero_percent'),
                        d.get('suffer_hurt_percent'), d.get('kill_cnt'), d.get('dead_cnt'), d.get('assist_cnt'), d.get('is_blue'), d.get('grade_of_rank'), d.get('lose_mvp'),
                        d.get('is_mvp'), d.get('pvp_level'), d.get('total_in_battle_coin'), d.get('used_time'), d.get('mvp_score_tth'), d.get('zone_area_id'), d.get('is_low_score'),
                        d.get('is_victory'),d.get('acnt_camp'), d.get('is_five_army'), d.get('game_result'), d.get('six_kill'), d.get('seven_kill'), d.get('eight_kill'),
                        d.get('game_score'),d.get('multi_camp_rank'), d.get('is_ai_pvp')) for d in user_battle_detail_list]
        db.executemany(insert_sql, detail_list)
        # return [{'open_id': d.get('open_id'), 'zone_area_id': d.get('zone_area_id')} for d in user_battle_detail_list]
        tup_user = []
        for d in user_battle_detail_list:
            if d.get('open_id') and d.get('zone_area_id'):
                tup_user += [(d.get('open_id'), d.get('zone_area_id'))]
        return tup_user
        # return [(d.get('open_id'), d.get('zone_area_id')) for d in user_battle_detail_list]

    else:
        raise Exception("error %s" % res)

def insert_user(user_list):
    sql = "INSERT IGNORE INTO `user` (`open_id`, `zone_area_id`) VALUES (%s, %s)"
    db.executemany(sql, user_list)


def update_user_fetch_status(open_id, zone_area_id):
    sql = "UPDATE user set fetched = 1 WHERE open_id=%s and zone_area_id = %s"
    db.executemany(sql, [(open_id, zone_area_id)])

def get_all_unfetched_user():
    sql = "select open_id, zone_area_id from user where fetched is null or fetched <> 1"
    return db.query(sql)

def get_battle_info(game_seq, game_svr_entity, relay_svr_entity):
    sql = "select id from user_battle_detail where game_seq=%s and game_svr_entity=%s and relay_svr_entity = %s"\
          % (game_seq, game_svr_entity, relay_svr_entity)
    return db.query(sql)


'''
1.我的所有比赛 & 比赛中玩家
2.我的好友
'''
def start_work():
    import warnings
    warnings.filterwarnings("ignore")
    q = Queue(100000)
    pending_users = get_all_unfetched_user()
    logger.info(pending_users)
    for item in pending_users:
        q.put((item.get('open_id'), item.get('zone_area_id')))

    if q.qsize() == 0:
        q.put((origin_user.get('open_id'), origin_user.get('zone_area_id')))

    while q.qsize() > 0:
        user_tup = q.get(0)
        logger.info("handle user ==> %s, queue size = %d" % (str(user_tup), q.qsize() + 1))
        fetch.update_config(open_id=user_tup[0], zone_area_id=user_tup[1])
        init_user()
        time.sleep(1)
        init_user_hero_info()
        time.sleep(1)
        new_user_list = init_battle_info_list_all()
        time.sleep(1)
        update_user_fetch_status(fetch.get_working_open_id(), fetch.get_working_zone_area_id())
        if new_user_list and len(new_user_list) > 0:
            insert_user(new_user_list)
            for item in new_user_list:
                logger.info("add user => %s" % str(item))
                q.put(item)

start_work()
