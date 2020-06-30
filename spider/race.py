# -*- coding: UTF-8 -*-


from spider import *
#from spider.common.get_cookie import get_cookie

class Race:

    def __init__(self,col):

        self.name = '赛马'
        self.session = requests.session()
        self.session.headers.update(headers)
        self.venues = ['S1','S2','ST','HV']
        self.col = col
        self.collect = mongodb.db[self.col]
        self.url = 'https://bet.hkjc.com/racing/getJSON.aspx'
        self.content_type = 'text/json; charset=utf-8'

        self.rtype = {'winplaodds': '独赢位置','qin':'连赢','qpl': '位置Q',}
        self.venue = None
        self.raceon = None
        self.map_page = {}
        self.init_venue()


    def update_one(self,condition,item):
        """更新数据"""
        try:

                self.collect.update_one(condition, {'$set': item}, upsert=True)
                logger.info('更新数据')

        except Exception as ex:
            logger.info(traceback.format_exc())

    def get_page(self):
        url = f'https://bet.hkjc.com/racing/script/rsdata.js?lang=ch&date={self.date}&venue={self.venue}&CV=L3.06R1f_1'
        response = self.session.get(url,timeout=timeout)

        text = response.text
        if not text[23:32] == 'Challenge':
            regex_page = re.compile('var mtgTotalRace = (.*);')
            regex_venue = re.compile('var mtgVenue = (.*);')
            page = regex_page.search(text)
            venue = regex_venue.search(text)

            if page:
                venue = eval(venue.group(1))
                page = int(page.group(1)) + 1
                self.map_page[venue] = page

                return page
            else:

                return None

        else:
            logger.info('响应不是json,获取cookie')
            get_cookie(self.session, url, response.text)
            return self.get_page()
    def init_venue(self):
        self.date = self.get_date()
        self.venue = self.get_venue()

        if self.venue:
            self.raceon = self.get_raceon()
            self.get_page()
        print(self.map_page)
    def get_date(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        return '2020-07-01'
    def get_venue(self):

        for venue in self.venues:
            param = {'type':'scratched','date': self.date,'venue':venue}
            response = self.session.get(self.url,params=param)
            text = response.text
            if not text[23:32] == 'Challenge':
                text = response.json()
                if text:

                    return text.get('SR')

            else:
                logger.info('响应不是json,获取cookie')
                get_cookie(self.session, self.url, response.text, para=param)
                return self.get_venue()



    def get_raceon(self):
        param = {'type': 'scratched'}
        param['date'] = self.date
        param['venue'] = self.venue
        try :
            response = self.session.get(self.url,params=param)
            text = response.text
            if not text[23:32] == 'Challenge':
                text = response.json()
                if text:
                    return  int(text.get('RAN_RACE')) + 1
                else:
                    return None
            else:
                logger.info('响应不是json,获取cookie')
                get_cookie(self.session, self.url, text, param)
                return self.get_raceon()
        except Exception as exc:
            logger.info(traceback.format_exc())

    def _get_race_info(self,page):


        url = f'https://bet.hkjc.com/racing/pages/odds_wp.aspx?lang=ch&date={self.date}&venue={self.venue}&raceno={page}'

        response = self.session.get(url)
        text = response.text
        if not text[23:32] == 'Challenge':

            return text
        else:
            logger.info('响应不是json,获取cookie')
            get_cookie(self.session, self.url, text,None)
            return self._get_race_info(page)

    def _parse_race_info(self,page,response):


        bs = BeautifulSoup(response, 'html.parser')
        desc = bs.find('span', attrs={'class': 'content'})
        if desc:
            desc = desc.get_text()

        regex_racech = re.compile('var infoDivideByRaceCh = (\[.*\])')
        regex_drawWgtByRace = re.compile("var drawWgtByRace = (.*);")
        regex_jockeysByRace = re.compile("var jockeysByRace = (.*);")
        regex_trainersByRace = re.compile("var trainersByRace = (.*);")
        infoDivideByRaceCh = regex_racech.search(response)
        #负磅
        drawWgtByRace = regex_drawWgtByRace.search(response)
        #骑师
        jockeysByRace  = regex_jockeysByRace.search(response)
        #练马师
        trainersByRace = regex_trainersByRace.search(response)
        if infoDivideByRaceCh:
            infoDivideByRaceCh  = eval(infoDivideByRaceCh.group(1))[page].split(';;')[0].split('|')[1:]
            drawWgtByRace1 = eval(drawWgtByRace.group(1))[page].split(';;')[2].split('|')[1:]
            gears = eval(drawWgtByRace.group(1))[page].split(';;')[1].split('|')[1:]

            jockeysByRace = eval(jockeysByRace.group(1))[page].split(';;')[0].split('|')[1:]
            trainersByRace = eval(trainersByRace.group(1))[page].split(';;')[0].split('|')[1:]
            item = {}
            item['description'] = desc
            item['raceon'] = self.raceon
            item['updateTime'] = datetime.datetime.now()
            item['raceInfo'] = []
            for i in range(0,len(infoDivideByRaceCh)):
                race_info = {}
                race_info['horseNumber'] = i + 1
                race_info['gear'] = gears[i]
                race_info['horseName'] = infoDivideByRaceCh[i]
                race_info['horseWeight'] = drawWgtByRace1[i]
                race_info['horseMan'] = jockeysByRace[i]
                race_info['horseTrainer'] = trainersByRace[i]
                item['raceInfo'].append(race_info)

            condition = {}
            condition['venue'] = self.venue
            condition['session'] = page
            condition['date'] = self.date
            condition['rtype'] = 'info'
            self.update_one(condition,item)

    def fetch_update_race_info(self):

        last_match_page = self.map_page[self.venue]
        for page in range(1,last_match_page):

            response = race._get_race_info(page)
            race._parse_race_info(page, response)




    def fetch(self):
        if self.venue:
            self.fetch_update_race_info()
            #for page in range(self.raceon,self.map_page[self.venue]):

                #self.tcetop(page)
    def get_winplaodds(self):
        url = f'https://bet.hkjc.com/racing/getJSON.aspx?type=winplaodds&date={self.date}&venue={self.venue}&start=1&end={self.map_page[self.venue]-1}'
        response =  self.session.get(url)
        text = response.text
        if not text[23:32] == 'Challenge':
            text = response.json()
            text = text['OUT'].split('@@@')[1:]

            for winpla in enumerate(text,1):
                item = {}
                item['win'] = []
                item['pla'] = []
                item['raceon'] = None
                item['updateTime'] = datetime.datetime.now()
                wins,plas = winpla[1].split('#')
                wins = wins.split(';')[1:]
                plas = plas.split(';')[1:]


                for win in wins:
                    win = win.split('=')
                    item['win'].append({'horseNumber': win[0],'odds': win[1],'trend':win[2]})

                for plas in plas:
                    plas = plas.split('=')
                    item['pla'].append({'horseNumber': plas[0],'odds': plas[1],'trend':plas[2]})

                condition = {}
                condition['date']= self.date
                condition['rtype'] = 'winpla'
                condition['session'] = winpla[0]
                condition['venue'] = self.venue
                self.update_one(condition,item)
        else:
            logger.info('响应不是json,获取cookie')
            get_cookie(sess, self.url, text, None)
            return self.get_winplaodds()


    def qintop(self,page):
        rtype = [
            'qintop', 'qinbank', 'qin',
            'qpltop', 'qplbank', 'qpl','tcetop']
        for r in rtype:
            url = f'https://bet.hkjc.com/racing/getJSON.aspx?type={r}&date={self.date}&venue={self.venue}&raceno={page}'
            response = self.session.get(url)
            text = response.text

            if not text[23:32] == 'Challenge':

                text = response.json()
                if r != 'qinbank' and r != 'qplbank':
                    item = {}
                    text = text['OUT'].split('@@@')[1:]
                    item['info'] = []
                    for winpla in enumerate(text, 1):

                        item['raceon'] = None
                        item['updateTime'] = datetime.datetime.now()
                        wins = winpla[1].split(';')[1:]
                        for win in wins:
                            win = win.split('=')
                            item['info'].append({'position': win[0], 'odds': win[1]})


                    condition = {}
                    condition['date'] = self.date
                    condition['rtype'] = r
                    condition['session'] = page
                    condition['venue'] = self.venue
                    self.update_one(condition, item)


                else:

                    text = text['OUT'].split(';')[1:]
                    item = {}
                    item['info'] = []
                    for winpla in enumerate(text, 1):


                        item['raceon'] = self.raceon
                        item['updateTime'] = datetime.datetime.now()
                        wins = winpla[1].split('|')
                        horseNumber,wins = wins[0],wins[1:]
                        for win in wins:
                            position = win.split('=')
                            item['info'].append({'horseNumber': horseNumber, 'position': position[0],'odds': position[1]})

                    condition = {}
                    condition['date'] = self.date
                    condition['rtype'] = r
                    condition['session'] = page
                    condition['venue'] = self.venue
                    self.update_one(condition, item)


            else:
                logger.info('响应不是json,获取cookie')
                get_cookie(sess, url, text, None)
                return self.qintop(page)

    def tcetop(self, page):
        rtype = [
            'tcetop','tcebank','tceinv',
            'tritop','tribank',
            'fftop','ffbank','ff',
            'qqttop', 'qqtbank',
            ]
        top = ['tcetop','tritop','ffttop','qqttop']
        bank = ['tcebank','tribank','ffbank', 'qqtbank']
        for r in rtype[5:6]:
            url = f'https://bet.hkjc.com/racing/getJSON.aspx?type={r}&date={self.date}&venue={self.venue}&raceno={page}'
            response = self.session.get(url)
            text = response.text

            if not text[23:32] == 'Challenge':

                text = response.json()
                if r in bank:
                    item = {}

                    text = text['OUT'].split(';')[1:]
                    item['info'] = []
                    for winpla in enumerate(text, 1):


                        item['raceon'] = self.raceon
                        item['updateTime'] = datetime.datetime.now()
                        wins = winpla[1].split('|')
                        horseNumber, wins = wins[0], wins[1:]
                        for win in wins:
                            position = win.split('=')
                            item['info'].append({'horseNumber': horseNumber, 'position': position[0],'odds': position[1]})


                    condition = {}
                    condition['date'] = self.date
                    condition['rtype'] = r
                    condition['session'] = page
                    condition['venue'] = self.venue
                    #self.update_one(condition, item)


                elif r == 'tceinv':

                    item = {}
                    item['info'] = []
                    item['raceon'] = self.raceon
                    item['updateTime'] = datetime.datetime.now()
                    text = text['OUT'].split(';')[1:]

                    for winpla in enumerate(text, 1):

                        wins = winpla[1].split('|')


                        horseNumber, wins = wins[0], wins[1:]
                        for win in wins:
                            position = win.split('=')
                            item['info'].append(
                                {'horseNumber': horseNumber, 'position': position[0], 'amount': position[1]})

                    condition = {}
                    condition['date'] = self.date
                    condition['rtype'] = r
                    condition['session'] = page
                    condition['venue'] = self.venue

                    self.update_one(condition, item)

                elif r in top:
                    item = {}
                    item['info'] = []
                    item['raceon'] = self.raceon
                    item['updateTime'] = datetime.datetime.now()
                    text = text['OUT'].split(';')[1:]
                    for winpla in enumerate(text, 1):


                        wins = winpla[1]
                        position = wins.split('=')
                        item['info'].append(
                            {'position': position[0], 'odds': position[1]})

                    condition = {}
                    condition['date'] = self.date
                    condition['rtype'] = r
                    condition['session'] = page
                    condition['venue'] = self.venue

                    self.update_one(condition, item)
            else:
                logger.info('响应不是json,获取cookie')
                get_cookie(sess, url, text, None)
                return self.qintop(page)

    def get_all(self,rtype,page,start):

        url = f'https://bet.hkjc.com/racing/getJSON.aspx?type={rtype}&date={self.date}&venue={self.venue}&raceno={page}&start={start}'

        try:
            response = self.session.get(url)
            text = response.text
            if not text[23:32] == 'Challenge':
                text = response.json()
                return text
            else:
                logger.info('响应不是json,获取cookie')
                get_cookie(sess, url, text, None)
                return self.get_all(rtype,page,start)

        except Exception as exc:
            logger.info(traceback.format_exc())

    def parse_all(self,page):
        rtype = ['tri', 'ff']
        for r in rtype:
            page = page
            start = 0
            item = {}
            item['info'] = []
            item['raceon'] = self.raceon
            item['updateTime'] = datetime.datetime.now()
            while True:
                response = race.get_all(r, page, start)

                response = response.get('OUT')
                if not response:
                    break
                start = start + 48
                response = response.split(';')[1:]
                for i in response:
                    position = i.split('=')
                    item['info'].append({'position':position[0],'odds':position[1]})

            condition = {}
            condition['date'] = self.date
            condition['rtype'] = r
            condition['session'] = page
            condition['venue'] = self.venue
            if item['info']:
                self.update_one(condition, item)

col = 'race'
race = Race(col=col)
race.fetch()










