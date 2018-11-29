#!/usr/bin/env python
# -*- coding' : 'utf-8 -*-
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class Fetcher:
    def __init__(self, openid, zone_area_id, ticket, key):
        self._openid = openid
        self._zone_area_id = zone_area_id
        self._init_openid = openid
        self._init_zone_area_id = zone_area_id
        self._ticket = ticket
        self._key = key

        self._headers = {
            'Host': 'game.weixin.qq.com',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B92 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN',
            'Accept-Language': 'zh-cn'
        }

        self._cookies = {
            'key': '%s' % self._key,
            'pass_ticket': '%s' % self._ticket,
            'uin': 'ODE1NDYzMjAw',
            'pgv_pvid': '5300987890',
            'eas_sid': 'r1o5z4T0H6Y0a4P6m5m2k4L0e2',
            'ts_uid': '7238923404',
            'PTTuserFirstTime': '1537920000000',
            'qb_qua': '',
            'Q-H5-GUID': '812ebcc9664546768e827d38406ce866',
            'qb_guid': '812ebcc9664546768e827d38406ce866',
            'pgv_pvi': '1324863488',
            'aics': 'qan9EEgwClB9cxB6bxMvnWbuYM0f3gM1fr6QG0v4',
            '3g_guest_id': '-8728220361318912000',
            'pgv_pvid_new': '085e9858eaa546e1657b1156c@wx.tenpay.com_15187d1acc3',
            'tvfe_boss_uuid': 'b5b23ccd7f5e3f98',
            'sd_cookie_crttime': '1527415810760',
            'sd_userid': '92261527415810760',
            'pac_uid': '0_5af45babd5609'
        }

    def update_config(self, open_id, zone_area_id):
        self._openid = open_id
        self._zone_area_id = zone_area_id

    def get_working_open_id(self):
        return self._openid

    def get_working_zone_area_id(self):
        return self._zone_area_id

    @staticmethod
    def _http_get(url, **kwargs):
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session.get(url, **kwargs)

    @staticmethod
    def _http_post(url, **kwargs):
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session.post(url, **kwargs)

    def get_user_info(self, zone_area_id=None):
        url = 'https://game.weixin.qq.com/cgi-bin/gamewap/getusermobagameindex'
        params = {
            'openid': '%s' % self._openid,
            'pass_ticket': '%s' % self._ticket,
            'zone_area_id': zone_area_id if zone_area_id else self._zone_area_id
        }

        headers = self._headers
        headers['Referer'] = 'https://game.weixin.qq.com/cgi-bin/h5/static/smobadynamic/dynamic.html?isFromWeappEntry=1&ssid=29&openid={}&abtest_cookie=AwABAAoACwAUAAMAI5ceAFeZHgCLmR4AAAA%3D&pass_ticket={}&wx_header=1'.format(self._openid, self._ticket)
        cookies = self._cookies

        response = self._http_get(url, params=params, headers = headers, cookies = cookies)
        return response.json()


    def get_hero_list(self):
        url = 'https://game.weixin.qq.com/cgi-bin/gamewap/gamemoba'
        params = {
            'pass_ticket': '%s' % self._ticket
        }

        data = {
            "appid": "wx95a3a4d7c627e07d"
        }

        headers = self._headers
        cookies = self._cookies

        response = self._http_post(url, params=params, data = data, headers = headers, cookies = cookies)
        return response.json()

    def get_user_hero_info(self, zone_area_id=None):
        url = 'https://game.weixin.qq.com/cgi-bin/gamewap/getmobauserheroinfo'
        params = {
            'openid': '%s' % self._openid,
            'zone_area_id': zone_area_id if zone_area_id else self._zone_area_id,
            'pass_ticket': '%s' % self._ticket
        }

        headers = self._headers
        headers['Referer'] = 'https://game.weixin.qq.com/cgi-bin/h5/static/smobadynamic/allhero.html?openid={}&zone_area_id={}&ssid=1021&uin=&key=&pass_ticket={}&abtest_cookie=AwABAAoACwAUAAMAI5ceAFeZHgCLmR4AAAA%3D&wx_header=1'.format(self._openid, self._zone_area_id, self._ticket)
        cookies = self._cookies

        response = self._http_get(url, params=params, headers = headers, cookies = cookies)
        return response.json()


    def get_battle_info_list(self, zone_area_id=None, offset=None, limit=None):
        url = 'https://game.weixin.qq.com/cgi-bin/gamewap/getusermobabattleinfolist'
        params = {
            'offset': offset if offset else 0,
            'limit': limit if limit else 10,
            'openid': '%s' % self._openid,
            'zone_area_id': zone_area_id if zone_area_id else self._zone_area_id,
            'pass_ticket': '%s' % self._ticket
        }

        headers = self._headers
        headers['Referer'] = 'https://game.weixin.qq.com/cgi-bin/h5/static/smobadynamic/allbattle.html?openid={}&zone_area_id={}&ssid=1021&uin=&key=&pass_ticket={}&wx_header=1'.format(self._openid, self._zone_area_id, self._ticket)
        cookies = self._cookies

        response = self._http_get(url, params=params, headers = headers, cookies = cookies)
        return response.json()

    def get_battle_info_detail(self, game_seq, game_svr_entity, relay_svr_entity):
        url = 'https://game.weixin.qq.com/cgi-bin/gamewap/getsmobabattledetail'
        params = {
            'openid': '%s' % self._openid,
            'game_svr_entity': game_svr_entity,
            'game_seq': game_seq,
            'relay_svr_entity': relay_svr_entity
        }

        headers = self._headers
        headers['Referer'] = 'https://game.weixin.qq.com/cgi-bin/h5/static/smobadynamic/index.html?game_svr_entity={}&game_seq={}&relay_svr_entity={}&openid={}&ssid=1021&abtest_cookie=AwABAAoACwAUAAMAI5ceAFeZHgCLmR4AAAA%3D&pass_ticket={}&wx_header=1'.format(game_svr_entity, game_seq, relay_svr_entity, self._openid, self._ticket)
        cookies = self._cookies

        response = self._http_get(url, params=params, headers = headers, cookies = cookies)
        return response.json()

