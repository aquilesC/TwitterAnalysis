from datetime import datetime, timedelta

from twitter_scraper.config import auth2, conn, cur


def get_trends(WOEID):
    trends = auth2.trends_place(WOEID)[0]
    date = trends['created_at']
    print('\t got {} trends'.format(len(trends['trends'])))
    for trend in trends['trends']:
        name = trend['name']
        tweet_volume = trend['tweet_volume']
        sql = 'INSERT INTO trends (date, name, tweet_volume, woid) values (?, ?, ?,?)'
        cur.execute(sql, (date, name, tweet_volume, WOEID))
        conn.commit()
    now = datetime.utcnow().isoformat()
    update_table = "UPDATE trends_explore SET last_retrieved = '{date}' WHERE woeid = {woeid}".format(date=now,woeid=WOEID)
    cur.execute(update_table)

    conn.commit()

def get_all_trends():
    sql = "SELECT woeid, last_retrieved, name FROM trends_explore"
    cur.execute(sql)
    woeids = cur.fetchall()
    for woeid in woeids:
        print('Getting trends of {}'.format(woeid[2]))
        if not woeid[1]:
            # This woeid was never fetched
            print('\t for the first time')
            get_trends(woeid[0])
        else:
            if datetime.utcnow() - datetime.strptime(woeid[1],"%Y-%m-%dT%H:%M:%S.%f") \
                    > timedelta(0,0,0,0,15):
                get_trends(woeid[0])

def add_interesting_trends():
    country_list = ['Argentina',
                    'Brazil',
                    'Chile',
                    'Colombia',
                    'Venezuela',
                    'Peru',
                    'Mexico']

    city_list = ['Buenos Aires',
                 'Córdoba',
                 'Rosario',
                 'São Paulo',
                 'Rio de Janeiro',
                 'Brasília']

    sql_unique = 'SELECT id FROM trends_explore WHERE woeid = {}'
    sql_add = 'INSERT INTO main.trends_explore (woeid, name) VALUES (?, ?)'
    available_trends = auth2.trends_available()
    for trend in available_trends:
        if trend['placeType']['code'] == 12: # Country
            if trend['name'] in country_list:
                cur.execute(sql_unique.format(trend['woeid']))
                data = cur.fetchall()
                if not data:
                    cur.execute(sql_add, (trend['woeid'], trend['name']))
                    conn.commit()

        elif trend['placeType']['code'] == 7: # Town
            if trend['name'] in city_list:
                cur.execute(sql_unique.format(trend['woeid']))
                data = cur.fetchall()
                if not data:
                    cur.execute(sql_add, (trend['woeid'], trend['name']))
                    conn.commit()

if __name__ == "__main__":
    get_all_trends()