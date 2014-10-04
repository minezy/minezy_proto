import time
import calendar
from datetime import date, timedelta


def prepare_date_range(params):
    ymd_range = []
    bYear = False
    bMonth = False
    bDay = False
    
    if params['start'] or params['end'] or params['year']:
        if params['year']:
            if params['month']:
                if params['day']:
                    # year month day
                    startdate = date(year=params['year'], month=params['month'], day=params['day'])
                    enddate = startdate
                else:
                    # year month only
                    startdate = date(year=params['year'], month=params['month'], day=1)
                    enddate = date(year=params['year'], month=params['month'], day=calendar.monthrange(params['year'], params['month'])[1])
            else:
                # year only
                startdate = date(year=params['year'], month=1, day=1)
                enddate = date(year=params['year'], month=12, day=31)
                
        else:
            # start/end times
            startdate = date.fromtimestamp(params['start'])
            enddate = date.fromtimestamp(params['end'])
            
        
        bWholeMonth = False
        if ((startdate.year==enddate.year) and (startdate.month==enddate.month) and
            (startdate.day==1) and (enddate.day==calendar.monthrange(enddate.year, enddate.month)[1])):
            bWholeMonth = True
        
        bForceDay = False
        bForceMonth = False
        bForceYear = False
        for c in params['count']:
            if c == 'DAY':
                bForceDay = True
                bForceMonth = False
                bForceYear = False
            elif c == 'MONTH':
                bForceDay = False
                bForceMonth = True
                bForceYear = False
            else:
                bForceDay = False
                bForceMonth = False
                bForceYear = True
            break
        
        delta = enddate - startdate
        for i in range(delta.days+1):
            d = startdate + timedelta(days=i)
            
            if (bForceYear):
                ymd_range.append(d.year)
                bYear = True
                
            elif (bForceMonth): 
                ymd_range.append(d.year*100 + d.month)
                bMonth = True
                
            elif (bForceDay):
                ymd_range.append(d.year*10000 + d.month*100 + d.day)
                bDay = True
                
            else:
                if ((d.year > startdate.year) and (d.year < enddate.year)):
                    ymd_range.append(d.year)
                    bYear = True
                    
                elif ((bWholeMonth) or 
                      ((d.year == startdate.year) and (d.month > startdate.month)) or 
                      ((d.year == enddate.year) and (d.month < enddate.month)) ):
                    ymd_range.append(d.year*100 + d.month)
                    bMonth = True
                    
                else:
                    ymd_range.append(d.year*10000 + d.month*100 + d.day)
                    bDay = True
                
        ymd_range = list(set(ymd_range))
    
    return ymd_range, bYear, bMonth, bDay


def prepare_date_clause(bYear, bMonth, bDay):
    query_str = ''
    
    if bYear:
        query_str += "(e)-[:YEAR]->(y)"
    if bMonth:
        if bYear:
            query_str += ","
        query_str += "(e)-[:MONTH]->(m)"
    if bDay:
        if bYear or bMonth:
            query_str += ","
        query_str += "(e)-[:DAY]->(d)"
        
    query_str += " WHERE ("
    
    if bYear:
        query_str += "y.num IN {ymd}"
    if bMonth:
        if bYear:
            query_str += " OR "
        query_str += "m.num IN {ymd}"
    if bDay:
        if bYear or bMonth:
            query_str += " OR "
        query_str += "d.num IN {ymd}"
        
    query_str += ") "
    
    return query_str

