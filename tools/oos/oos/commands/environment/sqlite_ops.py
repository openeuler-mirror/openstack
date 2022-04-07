import sqlite3

from oos.common import SQL_DB


def exe_query_sql(sql, *args):
    connect = sqlite3.connect(SQL_DB)
    cur = connect.cursor()
    try:
        cur.execute(sql, *args)
        result = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        connect.close()
    return result


def exe_sql(sql, *args):
    connect = sqlite3.connect(SQL_DB)
    cur = connect.cursor()
    try:
        cur.execute(sql, *args)
        connect.commit()
    except Exception as e:
        connect.rollback()
        print(e)
    finally:
        cur.close()
        connect.close()


def get_target_column(target, col_name):
    sql = "SELECT %s from resource where name=?" % col_name
    return exe_query_sql(sql, (target,))


def delete_target(target):
    sql = "DELETE from resource where name=?"
    exe_sql(sql, (target,))


def list_targets():
    sql = 'SELECT * FROM resource ORDER BY create_time'
    return exe_query_sql(sql)


def insert_target(*args):
    sql = "INSERT INTO resource VALUES (?,?,?,?,?,?,?,?)"
    exe_sql(sql, args)

