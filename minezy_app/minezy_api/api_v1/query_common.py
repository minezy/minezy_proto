import calendar
from minezy_api import app
from datetime import date, timedelta


def prepare_date_range(params):
    ymd_range = []
    
    bYear = False
    bMonth = False
    bDay = False
    
    bCountDay = False
    bCountMonth = False
    bCountYear = False
    for c in params['count']:
        if c == 'DAY':
            bCountDay = True
            bCountMonth = False
            bCountYear = False
        elif c == 'MONTH':
            bCountDay = False
            bCountMonth = True
            bCountYear = False
        elif c == 'YEAR':
            bCountDay = False
            bCountMonth = False
            bCountYear = True
        break
    
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

            # test if given start/end times are smaller range
            start = date.fromtimestamp(params['start'])
            end = date.fromtimestamp(params['end'])
            if start >= startdate and end <= enddate:
                startdate = start
                enddate = end

        else:
            # start/end times
            startdate = date.fromtimestamp(params['start'])
            enddate = date.fromtimestamp(params['end'])
            
        
        bWholeMonth = False
        if ((startdate.year==enddate.year) and (startdate.month==enddate.month) and
            (startdate.day==1) and (enddate.day==calendar.monthrange(enddate.year, enddate.month)[1])):
            bWholeMonth = True
        
        delta = enddate - startdate
        for i in range(delta.days+1):
            d = startdate + timedelta(days=i)
            
            if (bCountYear):
                ymd_range.append(d.year)
                bYear = True
                
            elif (bCountMonth): 
                ymd_range.append(d.year*100 + d.month)
                bMonth = True
                
            elif (bCountDay):
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
        
    elif params['count']:
        bYear = bCountYear
        bMonth = bCountMonth
        bDay = bCountDay
    
    return ymd_range, bYear, bMonth, bDay


def prepare_date_clause(bYear, bMonth, bDay, bNode=True, bPath=True, bWhere=True, bAnd=False, prefix='', default=''):
    query_str = ''
    
    if bPath:
        if bYear:
            if bNode:
                query_str += "(e)"
                
            query_str += "-->(y:Year)"
            
        if bMonth:
            if bYear:
                query_str += ",(e)"
            elif bNode:
                query_str += "(e)"

            query_str += "-->(m:Month)"
            
        if bDay:
            if bYear or bMonth:
                query_str += ",(e)"
            elif bNode:
                query_str += "(e)"
                
            query_str += "-->(d:Day)"
            
        if len(query_str):
            query_str += " "
        
    if bWhere and (bYear or bMonth or bDay):
        if bAnd:
            query_str += "AND ("
        else:
            query_str += "WHERE ("
        
        if bYear:
            query_str += "y.num IN {{ymd}}"
            
        if bMonth:
            if bYear:
                query_str += " OR "
            query_str += "m.num IN {{ymd}}"
            
        if bDay:
            if bYear or bMonth:
                query_str += " OR "
            query_str += "d.num IN {{ymd}}"
            
        query_str += ") "
    
    if len(query_str):
        if len(prefix):
            query_str = prefix + query_str
    else:
        query_str = default
        
    return query_str

def prepare_word_clause(word=[], prefix='', bNode=True, bPath=True, bWhere=True, bAnd=False, default=''):
    query_str = ''
    
    if (len(word)):
        if bPath:
            if bNode:
                query_str += "(w:Word)"
            else:
                query_str += ",(w:Word)"

            query_str += "-[rM:WORD_MONTH]-(wm:WordMonth)-[rW:WORDS]-(e:{0}Email) "
        if bWhere:
            if bAnd:
                query_str += "AND "
            else:
                query_str += "WHERE "

            query_str += "w.id IN {{word}} "

    if len(query_str):
        if len(prefix):
            query_str = prefix + query_str
    else:
        query_str = default
        
    print query_str

    return query_str
