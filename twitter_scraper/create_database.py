from twitter_scraper.config import conn, cur

def create_database():
    sql = """create table if not exists trends
(
  id           integer
    primary key
                       autoincrement,
  woid         integer default 1 not null,
  name         text not null,
  tweet_volume numeric default 0,
  date         TEXT not null
);"""
    cur.execute(sql)
    conn.commit()

    sql = """create table trends_explore
(
  id             integer
    primary key
  autoincrement,
  name           TEXT,
  woeid          int,
  last_retrieved TEXT
);"""
    cur.execute(sql)
    conn.commit()

    sql="""create unique index trends_explore_woeid_uindex
  on trends_explore (woeid);"""
    cur.execute(sql)
    conn.commit()

if __name__ == "__main__":
    create_database()