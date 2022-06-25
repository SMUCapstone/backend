# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 01:01:06 2022

@author: USER
"""
import pymysql
import pandas as pd

#db connection (vpc 서버)
def get_connection():
    conn = pymysql.connect(host = '34.64.56.32', user = 'root', password = '2017', 
                       db="capstoneDB", charset = 'utf8mb4')
    return conn


def testYoutuber():
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from youtuber"
    curs.execute(sql)
    result = curs.fetchall()
    data = pd.DataFrame(result)
    return data


def testContent():
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from content"
    curs.execute(sql)
    result = curs.fetchall()
    data = pd.DataFrame(result)
    return data


def testArchive():
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from archive"
    curs.execute(sql)
    result = curs.fetchall()
    data = pd.DataFrame(result)
    return data


def testCreateTable():
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "show tables"
    curs.execute(sql)
    result = curs.fetchall()
    data = pd.DataFrame(result)
    return data


def testRcommentTable(recognize):
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from " + recognize + ""
    curs.execute(sql)
    result = curs.fetchall()
    data = pd.DataFrame(result)
    return data
