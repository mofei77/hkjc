# -*- coding: UTF-8 -*-


from spider import *


class Prepare:
    def __init__(self,col=None):

        self.url = BASE_URL
        self.col = col
        self.content_type = 'application/json; charset=utf-8'
        self.collect = mongodb.db[self.col]

    def update_one(self,matchid,item):
        """更新数据"""
        try:

            if not self.isrollball:
                inplaydelay = item.get('inplaydelay')
                del item['inplaydelay']
                self.collect.update_one({'matchid': matchid,'inplaydelay':inplaydelay}, {'$set': item}, upsert=True)
                logger.info('更新数据')
            else:
                inplaydelay = item.get('inplaydelay')
                del item['inplaydelay']
                self.collect.update_one({'matchid': matchid,'inplaydelay':inplaydelay}, {'$set': item}, upsert=True)
                logger.info('更新数据')
        except Exception as ex:
            logger.info(traceback.format_exc())

    def update_one_by_jsontype(self,jsontype,item):
        try:
            self.collect.update_one(jsontype, {'$set': item}, upsert=True)

            logger.info(f'冠军更新数据,暂停{fresh_by_jsontype}秒')
            #time.sleep(fresh_by_jsontype)
        except Exception as ex:
            logger.info(traceback.format_exc())
    def get_matchid(self):
        try:
            gids = []
            response = self.session.get(self.url,params=self.json_type, timeout=timeout)
            if response.status_code == 200 and self.content_type == response.headers['Content-Type']:
                response = response.json()
                for reslut in response:

                    gids.append(reslut.get('matchID'))
                return gids
            else:

                logger.info('响应不是json,获取cookie')
                # set cookie
                get_cookie(self.session,self.url,response.text,self.json_type)
                return self.get_matchid()
        except Exception as ex:
            logger.info(traceback.format_exc())
            return self.get_matchid()

    def handle_matchid(self,matchid):
        para={'jsontype': 'odds_allodds.aspx','matchid':matchid}
        try:
            response = self.session.get(self.url, timeout=timeout,params=para)
            if response.status_code == 200 and self.content_type == response.headers['Content-Type']:
                response = response.json()
                return response
            else:

                logger.info('响应不是json,获取cookie')
                get_cookie(self.session, self.url, response.text,para=para)
                return self.handle_matchid(matchid)
        except Exception as ex:
            return self.handle_matchid(matchid)


    def get_rollball_matchid(self):
        para = {'jsontype': 'odds_inplay.aspx'}
        try:
            gids = []
            response = self.session.get(self.url,params=para, timeout=timeout)
            if response.status_code == 200 and self.content_type == response.headers['Content-Type']:
                response = response.json()

                for reslut in response:
                    #if reslut.get('matchStatus') != 'Defined':
                    gids.append(reslut.get('matchID'))
                return gids
            else:

                logger.info('响应不是json,获取cookie' + traceback.format_exc())
                # set cookie
                get_cookie(self.session,self.url,response.text)
                return self.get_rollball_matchid()
        except Exception as ex:
            logger.info(ex.args)
            return self.get_rollball_matchid()

    def handle_rollball_matchid(self,matchid):
        para={'jsontype': 'odds_inplay_all.aspx','matchid': matchid}
        try:
            response = self.session.get(self.url,params=para, timeout=timeout)
            if response.status_code == 200 and self.content_type == response.headers['Content-Type']:
                responses = response.json()
                for response in responses:
                    if response.get('matchID') == matchid:
                        return response
                return response
            else:

                logger.info('响应不是json,获取cookie' + traceback.format_exc())
                get_cookie(self.session, self.url, response.text,para=para)
                return self.handle_rollball_matchid(matchid)
        except Exception as ex:
            return self.handle_rollball_matchid(matchid)

    def fetch(self):
        gids = self.get_matchid()
        print(len(gids))
        if not gids:
            logger.info(f'{self.name}暂无赛事暂停{stop}')
            time.sleep(stop)
        for gid in gids:
            response = self.handle_matchid(gid)
            item = self.parse_response(response)
            if item:

                self.update_one(gid, item)

    def fetch_rollball(self):
        gids = self.get_rollball_matchid()

        if not gids:
            logger.info(f'{self.name}暂无赛事暂停{rollball_stop}')
            time.sleep(rollball_stop)
        for gid in gids:
            response = self.handle_rollball_matchid(gid)
            item = self.parse_rollball_response(response)
            if item:
                self.update_one(gid,item)

    def parse_response(self, response):
        for item in response:
            if item.get('anyInplaySelling') and item.get('matchStatus') == 'Defined':
                result = self.parse_current_match(item)
                return result
    def parse_rollball_response(self,response):

        result = self.parse_current_match(response)
        return result

    def parse_current_match(self,item):


        item['updateTime'] = datetime.datetime.now()
        if not getattr(self,'isrollball'):
            inplaypools_name = 'definedPools'
        else:
            inplaypools_name = 'inplayPools'
            inplayPools = item.get('inplayPools')
            remove = []
            for key in item:
                if 'odds' in key:
                    if key[:-4].upper() in inplayPools:
                        pass
                    else:
                        remove.append(key)

            for key in remove:
                del item[key]
        inplay_pools = item.get(inplaypools_name)
        for inplay in inplay_pools:

            inplay_key = inplay.lower() + 'odds'
            odds = {}
            if item.get(inplay_key) and inplay_key == 'hadodds':
                # 主客和
                temp =  item.get(inplay_key)
                odds['homewin'] = temp.get('H')[4:]
                odds['awaywin'] = temp.get('A')[4:]
                odds['draw'] = temp.get('D')[4:]
                odds['status'] = temp.get('POOLSTATUS')
                odds['title'] = map_item.get(inplay_key)
                item[inplay_key] = odds


            elif item.get(inplay_key) and inplay_key == 'fhaodds':
                # 半场主客和
                temp = item.get(inplay_key)
                odds['homewin'] = temp.get('H')[4:]
                odds['awaywin'] = temp.get('A')[4:]
                odds['draw'] = temp.get('D')[4:]
                odds['status'] = temp.get('POOLSTATUS')
                odds['title'] = map_item.get(inplay_key)
                item[inplay_key] = odds

            elif item.get(inplay_key) and inplay_key == 'hhaodds':
                # 让球主客和
                temp = item.get(inplay_key)
                odds['homewin'] = temp.get('H')[4:]
                odds['awaywin'] = temp.get('A')[4:]
                odds['draw'] = temp.get('D')[4:]
                odds['status'] = temp.get('POOLSTATUS')
                odds['title'] = map_item.get(inplay_key)

                item[inplay_key] = odds

            elif item.get(inplay_key) and inplay_key == 'hdcodds':
                # 让球
                temp = item.get(inplay_key)
                point = temp.get('HG')
                if '/' in point:
                    slice_point = point.split('/')
                    point = point if slice_point[0] != slice_point[1] else slice_point[0]
                odds['homewin'] = temp.get('H')[4:]
                odds['awaywin'] = temp.get('A')[4:]
                odds['point'] = point

                odds['status'] = temp.get('POOLSTATUS')
                odds['title'] = map_item.get(inplay_key)

                item[inplay_key] = odds

            elif item.get(inplay_key) and inplay_key == 'hilodds':
                # 入球大细
                temp = item.get(inplay_key)
                odds['info'] = []
                linelist = temp.get('LINELIST')
                for i in linelist:
                    point = i.get('LINE')
                    if '/' in point:
                        slice_point = point.split('/')
                        point = point if slice_point[0] != slice_point[1] else slice_point[0]
                    odds['info'].append({'gt': i.get('H')[4:],'lt': i.get('L')[4:],'point': point})

                odds['status'] = temp['POOLSTATUS']
                odds['title'] = map_item.get(inplay_key)
                item[inplay_key] = odds

            elif item.get(inplay_key) and inplay_key == 'fhlodds':
                # 半场入球大细
                temp = item.get(inplay_key)
                odds['info'] = []
                linelist = temp.get('LINELIST')
                for i in linelist:
                    point = i.get('LINE')
                    if '/' in point:
                        slice_point = point.split('/')
                        point = point if slice_point[0] != slice_point[1] else slice_point[0]
                    odds['info'].append({'gt': i.get('H')[4:], 'lt': i.get('L')[4:], 'point': point})

                odds['sataus'] = temp['POOLSTATUS']
                odds['title'] = map_item.get(inplay_key)
                item[inplay_key] = odds


            elif item.get(inplay_key) and inplay_key == 'chlodds':
                # 角球大细
                temp = item.get(inplay_key)
                odds['info'] = []
                linelist = temp.get('LINELIST')
                for i in linelist:
                    point = i.get('LINE')
                    if '/' in point:
                        slice_point = point.split('/')
                        point = point if slice_point[0] != slice_point[1] else slice_point[0]
                    odds['info'].append({'gt': i.get('H')[4:], 'lt': i.get('L')[4:], 'point': point})

                odds['sataus'] = temp['POOLSTATUS']
                odds['title'] = map_item.get(inplay_key)
                item[inplay_key] = odds


            elif item.get(inplay_key) and inplay_key == 'crsodds':
                # 波胆
                temp = item.get(inplay_key)
                odds['home'] = []
                odds['away'] = []
                odds['draw'] = []

                map_csrodds = {
                    'S0100':'home','S0200':'home','S0201':'home','S0300':'home','S0301':'home','S0302':'home','S0400':'home','S0401':'home','S0402':'home','S0500':'home','S0501':'home','S0502':'home',
                    'S0001':'away','S0002':'away', 'S0102':'away','S0003': 'away', 'S0103': 'away','S0203': 'away', 'S0004': 'away', 'S0104': 'away', 'S0204': 'away', 'S0005': 'away','S0105': 'away', 'S0205': 'away',
                    'S0000': 'draw','S0101': 'draw','S0202': 'draw','S0303': 'draw',
                    'SM1MA': 'away','SM1MH': 'home','SM1MD':'draw'

                }
                map_other = {'1:A': 'other','1:D': 'other','1:H': 'other',}
                for key, value in temp.items():
                    if '@' in value:
                        score = key[2] + ':' + key[-1]
                        score = map_other.get(score) or score
                        info = {'name': score,'odds': value[4:]}
                        odds[map_csrodds.get(key)].append(info)

                odds['title'] = map_item.get(inplay_key)
                odds['sataus'] = temp['POOLSTATUS']
                item[inplay_key] = odds



            elif item.get(inplay_key) and inplay_key == 'fcsodds':
                # 半场波胆
                temp = item.get(inplay_key)
                odds['home'] = []
                odds['away'] = []
                odds['draw'] = []

                map_csrodds = {
                    'S0100':'home','S0200':'home','S0201':'home','S0300':'home','S0301':'home','S0302':'home','S0400':'home','S0401':'home','S0402':'home','S0500':'home','S0501':'home','S0502':'home',
                    'S0001':'away','S0002':'away', 'S0102':'away','S0003': 'away', 'S0103': 'away','S0203': 'away', 'S0004': 'away', 'S0104': 'away', 'S0204': 'away', 'S0005': 'away','S0105': 'away', 'S0205': 'away',
                    'S0000': 'draw','S0101': 'draw','S0202': 'draw','S0303': 'draw',
                    'SM1MA': 'away','SM1MH': 'home','SM1MD':'draw'

                }
                map_other = {'1:A': 'other','1:D': 'other','1:H': 'other',}
                for key, value in temp.items():
                    if '@' in value:
                        score = key[2] + ':' + key[-1]
                        score = map_other.get(score) or score
                        info = {'name': score,'odds': value[4:]}
                        odds[map_csrodds.get(key)].append(info)

                odds['title'] = map_item.get(inplay_key)
                odds['status'] = temp['POOLSTATUS']
                item[inplay_key] = odds


            elif item.get(inplay_key) and inplay_key == 'ntsodds':
                # 下一队进球
                if item.get(inplay_key):
                    descriptions = item.get(inplay_key)
                    odds['info'] = []

                    for description in descriptions:

                        odds['info'].append({'home':description.get('H')[4:],'away':description.get('A')[4:],'N':description.get('N')[4:]})
                        odds['status'] = description['POOLSTATUS']
                        odds['title'] = map_item.get(inplay_key)
                    item[inplay_key] = odds


            elif item.get(inplay_key) and inplay_key == 'ftsodds':
                # 第一队入球
                temp = item.get(inplay_key)
                odds['home'] = temp.get('H')[4:]
                odds['away'] = temp.get('A')[4:]
                odds['N'] = temp.get('N')[4:]
                odds['title'] = map_item.get(inplay_key)
                odds['status'] = temp['POOLSTATUS']
                item[inplay_key] = odds


            elif item.get(inplay_key) and inplay_key == 'ttgodds':
                # 总入球
                temp = item.get(inplay_key)
                odds['info'] = []
                for key, value in temp.items():
                    if '@' in value:

                        odds['info'].append({'name': key,'odds': value[4:]})
                odds['title'] = map_item.get(inplay_key)
                odds['status'] = temp['POOLSTATUS']
                item[inplay_key] = odds


            elif item.get(inplay_key) and inplay_key == 'ooeodds':
                # 入球单双
                temp = item.get(inplay_key)
                odds['info'] = [{'name': '单','odds': temp.get('O')[4:]},{'name': '双','odds': temp.get('E')[4:]}]
                odds['title'] = map_item.get(inplay_key)
                item[inplay_key] = odds

            elif item.get(inplay_key) and inplay_key == 'hftodds':
                # 半全场
                temp = item.get(inplay_key)
                map_hftodds = {
                    'HD': '主-和','HA': '主-客','HH': '主-主',
                    'AD': '客-和','AH': '客-主','AA': '客-客',
                    'DH': '和-主','DA': '和-客','DD': '和-和'}
                odds['info'] = []
                for key, value in temp.items():
                    if '@' in value:
                        odds['info'].append({'name': key,'odds': value[4:],'CH':map_hftodds.get(key)})
                odds['title'] = map_item.get(inplay_key)
                item[inplay_key] = odds

            elif item.get(inplay_key) and inplay_key == 'spcodds':
                #特别项目
                descriptions = item.get(inplay_key)
                info = []
                for description in descriptions:
                    desc = {}
                    desc['title'] = map_item.get(inplay_key)
                    desc['item'] = description.get('ITEM')
                    desc['inplay'] = description.get('INPLAY')
                    desc['itemech'] = description.get('ITEMCH')
                    desc['itemeen'] = description.get('ITEMEN')
                    desc['status'] = description.get('POOLSTATUS')
                    desc['info'] = []
                    for sellist in description['SELLIST']:
                        sel = {'odds': sellist['ODDS'][4:],'sel': sellist['SEL'],'itemech': sellist.get('CONTENTCH'),'selstatus':sellist.get('SELSTATUS') }
                        desc['info'].append(sel)
                    info.append(desc)
                item[inplay_key] = info

            elif item.get(inplay_key) and inplay_key == 'fgsodds':
                # 首名入球
                description = item.get(inplay_key)
                desc = {}
                desc['title'] = map_item.get(inplay_key)
                desc['inplay'] = description.get('INPLAY')
                desc['status'] = description.get('POOLSTATUS')
                desc['info'] = []
                for sellist in description['SELLIST']:
                    sel = {'odds': sellist['ODDS'][4:], 'sel': sellist['SEL'], 'itemech': sellist.get('CONTENTCH'),
                           'itemen': sellist.get('CONTENTEN')}

                    desc['info'].append(sel)
                item[inplay_key] = desc
            elif item.get(inplay_key) and inplay_key == 'tqlodds':
                #晋级队伍
                description = item.get(inplay_key)
                desc = {}
                desc['title'] = map_item.get(inplay_key)
                desc['inplay'] = description.get('INPLAY')
                desc['status'] = description.get('POOLSTATUS')
                desc['homewin'] = description.get('H')[4:]
                desc['awaywin'] = description.get('A')[4:]
                item[inplay_key] = desc
        item['sportid'] = 1
        item['updateTime'] = datetime.datetime.now()
        if item.get('channel'): del item['channel']
        del item['matchID']
        return item


    def champion(self,param):

        try:
            response = self.session.get(self.url,params=param)
            if response.status_code == 200 and self.content_type == response.headers['Content-Type']:
                response = response.json()

                return response
            else:

                logger.info('响应不是json,获取cookie')
                # set cookie
                get_cookie(self.session, self.url, response.text, param)
                return self.champion(param)

        except Exception as ex:
            logger.info(traceback.format_exc())

    def fetch_champion(self):
        params = [
            {'jsontype': 'odds_chp.aspx'},
            {'jsontype': 'tournament.aspx', 'tourn': '1644'},
            #{'jsontype': 'tournament.aspx', 'tourn': '1658'}
        ]

        for i in params:
            response = self.champion(i)
            if isinstance(response,list):
                key = 'chpodds'
                for item in response:
                    if item.get(key) :
                        odds = deepcopy(item.get(key))
                        sellist  = item[key]['SELLIST']
                        del item[key]['SELLIST']
                        info = []
                        for sell in sellist:
                            if sell['ODDS'][4:] != 'LSE':
                                info.append({'name': sell.get('CONTENTCH'),'odds': sell.get('ODDS')[4:]})
                        item[key]['info'] = info
                        odds['title'] = map_item[key]
                        tournamentID = item.get('tournamentID')
                        jsontype = {'tournamentID':tournamentID,'jsontype': key}
                        item['updateTime'] = datetime.datetime.now()
                        self.update_one_by_jsontype(jsontype,item)
            elif isinstance(response,dict):
                tps_key = 'tpsodds'
                chp_key = 'chpodds'
                if response.get(tps_key):
                    tpsodds = response.get(tps_key)

                    for players in tpsodds:
                        info = []
                        sellist = players['SELLIST']
                        del players['SELLIST']
                        for  sell in sellist:
                            if sell['ODDS'][4:] != 'LSE':
                                info.append({'name': sell.get('CONTENTCH'),'odds': sell.get('ODDS')[4:]})
                        players['info'] = info

                    response[tps_key] = tpsodds

                if response.get(chp_key):
                    chpodds = response.get(chp_key)

                    sellist = chpodds['SELLIST']
                    del chpodds['SELLIST']
                    info = []
                    for sell in sellist:
                        if sell['ODDS'][4:] != 'LSE':
                            info.append({'name': sell.get('CONTENTCH'), 'odds': sell.get('ODDS')[4:]})
                    chpodds['info'] = info

                    response[chp_key] = chpodds


                tournamentID = response.get('tournamentID')
                jsontype = {'tournamentID': tournamentID, 'jsontype': 'league'}
                response['updateTime'] = datetime.datetime.now()
                self.update_one_by_jsontype(jsontype, response)

class Soccer(Prepare):
    def __init__(self,col=None,isrollball=False,name=None):
        super(Soccer,self).__init__(col)
        self.name = name
        self.isrollball = isrollball
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.json_type = {
            'jsontype': 'odds_allodds.aspx',
            'matchid': 'default'}



if __name__ == '__main__':
    soccer = Soccer(col='rollball',isrollball=True,name='足球走地盘')
    soccer2 = Soccer(col='sports',isrollball=False,name='足球')
    soccer3 = Soccer(col='sports', isrollball=False, name='足球')

    def main1():
        while True:
            soccer.fetch_rollball()
            time.sleep(5)
    def main2():
        while True:
            #soccer2.fetch()
            soccer3.fetch_champion()
            time.sleep(100)
    import threading

    t1 = threading.Thread(target=main1,)
    t2 = threading.Thread(target=main2, )
    t1.start()





