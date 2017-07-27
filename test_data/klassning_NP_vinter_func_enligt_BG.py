# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 09:55:12 2013

@author: a001693
"""

def klassning_NP_vinter(TYP,year_start,year_end,data_dict,infil_stationer):
    '''Statusklassa DIN, DIP, tot-N och tot-P i (TYP,startår,slutår,dictionary) allt som strängar'''

    
    #   ¸.·´¯`·.´¯`·.¸¸.·´¯`·.¸><(((º>   ¸.·´¯`·.´¯`·.¸¸.·´¯`·.¸><(((º>   ¸.·´¯`·.´¯`·.¸¸.·´¯`·.¸><(((º>
    
    import pyodbc
    import os
    import numpy as np
    from korta_script.index_alla import index_alla
    from korta_script.intersect import intersect
    import codecs
    
    min_antal_varden = 2
    #min_antal_varden_vasterhavet = 4 (dec-mars gäller enligt föreskriften, gammalt i bedömningsgrunderna (dec-feb))
    min_antal_varden_vasterhavet = 3
    
    depthlimit = u'5'
    
    # FÖR ATT OVAN IMPORT AV korta_script SKA FUNKA SÅ MÅSTE EN SÖKVÄG LÄGGAS TILL I PYTHONPATH:
    # File -> PYTHONPATH manager -> + add path '\\winfs-proj\proj\havgem\NEMO\python_projekt\korta_script'
    
    
    # Västerhavet ['1n','1s','2','3','4','25','5','6']
    # 1n, 1s, 2-11, 12s, 12n, 13-25
    ## TYP = '2'
    # Gjorda: 12s, 15, 16, 17, 18, 19, 20, 21, 22, 23 
    
    
    
    # TYP = '1n'
    
    ## year_start = '1997' # första året då data hämtas
    ## year_end = '2012' # sista året då data hämtas
    
    
    
    #                                                           ─▄───────▄█▄───────▄─
    #       ███████ ]▄▄▄▄▄▄▄▄▃    - - ❍                        ▐█▌──▄──█████──▄──▐█▌
    #   ▂▄▅█████████▅▄▃▂                                       ─█──███▄▄███▄▄███──█─
    # I███████████████████].                                    ░█░░█▄█▄█▀▒▀█▄█▄█░░█░
    #    ◥⊙▲⊙▲⊙▲⊙▲⊙▲⊙▲⊙◤…                                        ██▄▄█▄█▄█▒▒▒█▄█▄█▄▄██
    
    
    
    
    os.chdir('\\\\winfs-proj\\proj\\havgem\\NEMO\\python_projekt\\Statusklassning\\')
    
    # from klassning_NP_sommar_func import klassning_NP_sommar
    # from klassning_siktdjup_func import klassning_siktdjup
    # from klassning_syrgas_func import klassning_syrgas
    # from klassning_biovolym_func import klassning_biovolym
    # from klassning_klorofyll_func import klassning_klorofyll
    # from klassning_klorofyll_ostersjon_func import klassning_klorofyll_ostersjon
    
    
    # KOLUMNER
    # statkols = ['FID_1','STATION','LATITUD','LONGITUD','lat_dd','long_dd','FID_2','NAMN','Vattendist','OMRTYP','DATUM','OLD_HID','TYP_NFS06','HID','DIST_CD','EU_CD','District','Country','TYP_HAVDIR','TYP06_TXT','TYP_EGEN','Shape_Leng','Shape_Area']
    # 1 - 'STATION'  (stationsnamn)
    # 7 - 'NAMN'  (namn på vattenförekomst)
    # 15 - 'EU_CD'  (EU_CD id för vattenförekomst)
    # 20 - 'TYP_EGEN'  (typ som stationen hör till)
    # 21 - 'EXTRA_KOD'  (kod för om stationen hamnat utanför i GIS-joinen, L=Land, U=Utsjö
    # 2 - 'LATITUD'
    # 3 - 'LONGITUD'
    
    station_dict = {'STATION':[],'SEAAREA':[],'EU_CD':[],'TYP':[],'EXTRA_CODE':[],'LATITUD':[],'LONGITUD':[]}
    
    # infil_stat = open(infil_stationer,'r')
    infil_stat = codecs.open(infil_stationer,'r',encoding = 'cp1252')
    # filen verkar vara i latin1 redan, vilket borde vara ok.
    
    antalrader = 0
    for rows in infil_stat:
        
        rowdata = []
        if antalrader >= 1: # ej Header
            if rows[-1] == '\n':
                rowdata = rows[:-1].split('\t')  # [:-1] tar bort \n på slutet
            else:
                rowdata = rows.split('\t')
        
            station_dict['STATION'].append(rowdata[1])
            station_dict['SEAAREA'].append(rowdata[7])
            station_dict['EU_CD'].append(rowdata[15])
            station_dict['TYP'].append(rowdata[20])
            station_dict['EXTRA_CODE'].append(rowdata[21])
            station_dict['LATITUD'].append(rowdata[2])
            station_dict['LONGITUD'].append(rowdata[3])
        
        antalrader += 1
    
    infil_stat.close()
    
    
    index_typ = index_alla(station_dict['TYP'],TYP)
    
    # stations = [u'Å17'.encode('latin1'),u'ANHOLT E'.encode('latin1'),'XXX']
    stations_typ = {}
    
    for ind in index_typ:
        stations_typ[station_dict['STATION'][ind]] = [station_dict['EU_CD'][ind],station_dict['SEAAREA'][ind]]
    
    
    
    # testa sql "in"
    stations_typ_list = stations_typ.keys()
    for stat in stations_typ_list:
        if stat == stations_typ_list[0]:
            stationslista = u"'" + stat + u"'"
        else:
            stationslista = stationslista + u"," + u"'" + stat + u"'"
    
    
    stationslista
    print stationslista
    
    
    del stations_typ_list
    
    # Läs in referensvärden per område, då kommer månaderna med också...
    
    ref_matrix = {'din':{'typ':[],'ref':[],'month':[],'saltmax':[],'HG':[],'GM':[],'MO':[],'OD':[]},'dip':{'typ':[],'ref':[],'month':[],'saltmax':[],'HG':[],'GM':[],'MO':[],'OD':[]},\
                'totn':{'typ':[],'ref':[],'month':[],'saltmax':[],'HG':[],'GM':[],'MO':[],'OD':[]},'totp':{'typ':[],'ref':[],'month':[],'saltmax':[],'HG':[],'GM':[],'MO':[],'OD':[]}}
    
    
    infil_ref_din = open('\\\\winfs-proj\\proj\\havgem\\NEMO\\python_projekt\\Statusklassning\\BG\\txt\\din_vinter.txt','r')
    
    antalrader = 0
    for rows in infil_ref_din:
        
        rowdata = []
        temp_month = []
        if antalrader >= 1: # ej Header
            if rows[-1] == '\n':
                rowdata = rows[:-1].split('\t')  # [:-1] tar bort \n på slutet
            else:
                rowdata = rows.split('\t')
            
            ref_matrix['din']['typ'].append(rowdata[0])
            
            ref_matrix['din']['ref'].append(rowdata[1])
            
            temp_month = rowdata[6].replace('"','').split(';')
            month_string = []
            for m in temp_month:
                if m == temp_month[0]: # första, lägg inte komma framför, samt ej append
                    month_string = ("'" + '%02i' % int(m)) + "'"
                else:
                    month_string = month_string + (",'" + '%02i' % int(m)) + "'"
            
            
            ref_matrix['din']['month'].append(month_string)
                
            ref_matrix['din']['saltmax'].append(float(rowdata[11]))
            ref_matrix['din']['HG'].append(float(rowdata[7]))
            ref_matrix['din']['GM'].append(float(rowdata[8]))
            ref_matrix['din']['MO'].append(float(rowdata[9]))
            ref_matrix['din']['OD'].append(float(rowdata[10]))
            
        antalrader += 1
    
    
    infil_ref_din.close()
    
    
    # läs in dip, totn, totp också...
    
    # DIP
    infil_ref_dip = open('\\\\winfs-proj\\proj\\havgem\\NEMO\\python_projekt\\Statusklassning\\BG\\txt\\dip_vinter.txt','r')
    
    antalrader = 0
    for rows in infil_ref_dip:
        
        rowdata = []
        temp_month = []
        if antalrader >= 1: # ej Header
            if rows[-1] == '\n':
                rowdata = rows[:-1].split('\t')  # [:-1] tar bort \n på slutet
            else:
                rowdata = rows.split('\t')
            
            ref_matrix['dip']['typ'].append(rowdata[0])
            
            ref_matrix['dip']['ref'].append(rowdata[1])
            
            temp_month = rowdata[6].replace('"','').split(';')
            month_string = []
            for m in temp_month:
                if m == temp_month[0]: # första, lägg inte komma framför, samt ej append
                    month_string = ("'" + '%02i' % int(m)) + "'"
                else:
                    month_string = month_string + (",'" + '%02i' % int(m)) + "'"
            
            
            ref_matrix['dip']['month'].append(month_string)
                
            ref_matrix['dip']['saltmax'].append(float(rowdata[11]))
            ref_matrix['dip']['HG'].append(float(rowdata[7]))
            ref_matrix['dip']['GM'].append(float(rowdata[8]))
            ref_matrix['dip']['MO'].append(float(rowdata[9]))
            ref_matrix['dip']['OD'].append(float(rowdata[10]))
            
        antalrader += 1
    
    
    infil_ref_dip.close()
    
    
    # Tot-N
    infil_ref_totn = open('\\\\winfs-proj\\proj\\havgem\\NEMO\\python_projekt\\Statusklassning\\BG\\txt\\totn_vinter.txt','r')
    
    antalrader = 0
    for rows in infil_ref_totn:
        
        rowdata = []
        temp_month = []
        if antalrader >= 1: # ej Header
            if rows[-1] == '\n':
                rowdata = rows[:-1].split('\t')  # [:-1] tar bort \n på slutet
            else:
                rowdata = rows.split('\t')
            
            ref_matrix['totn']['typ'].append(rowdata[0])
            
            ref_matrix['totn']['ref'].append(rowdata[1])
            
            temp_month = rowdata[6].replace('"','').split(';')
            month_string = []
            for m in temp_month:
                if m == temp_month[0]: # första, lägg inte komma framför, samt ej append
                    month_string = ("'" + '%02i' % int(m)) + "'"
                else:
                    month_string = month_string + (",'" + '%02i' % int(m)) + "'"
            
            
            ref_matrix['totn']['month'].append(month_string)
                
            ref_matrix['totn']['saltmax'].append(float(rowdata[11]))
            ref_matrix['totn']['HG'].append(float(rowdata[7]))
            ref_matrix['totn']['GM'].append(float(rowdata[8]))
            ref_matrix['totn']['MO'].append(float(rowdata[9]))
            ref_matrix['totn']['OD'].append(float(rowdata[10]))
            
        antalrader += 1
    
    
    infil_ref_totn.close()
    
    
    # Tot-P
    infil_ref_totp = open('\\\\winfs-proj\\proj\\havgem\\NEMO\\python_projekt\\Statusklassning\\BG\\txt\\totp_vinter.txt','r')
    
    antalrader = 0
    for rows in infil_ref_totp:
        
        rowdata = []
        temp_month = []
        if antalrader >= 1: # ej Header
            if rows[-1] == '\n':
                rowdata = rows[:-1].split('\t')  # [:-1] tar bort \n på slutet
            else:
                rowdata = rows.split('\t')
            
            ref_matrix['totp']['typ'].append(rowdata[0])
            
            ref_matrix['totp']['ref'].append(rowdata[1])
            
            temp_month = rowdata[6].replace('"','').split(';')
            month_string = []
            for m in temp_month:
                if m == temp_month[0]: # första, lägg inte komma framför, samt ej append
                    month_string = ("'" + '%02i' % int(m)) + "'"
                else:
                    month_string = month_string + (",'" + '%02i' % int(m)) + "'"
            
            
            ref_matrix['totp']['month'].append(month_string)
                
            ref_matrix['totp']['saltmax'].append(float(rowdata[11]))
            ref_matrix['totp']['HG'].append(float(rowdata[7]))
            ref_matrix['totp']['GM'].append(float(rowdata[8]))
            ref_matrix['totp']['MO'].append(float(rowdata[9]))
            ref_matrix['totp']['OD'].append(float(rowdata[10]))
            
        antalrader += 1
    
    
    infil_ref_totp.close()
    
    
    index_din_ref_typ = ref_matrix['din']['typ'].index(TYP)
    # alla index borde vara samma...
    index_dip_ref_typ = ref_matrix['dip']['typ'].index(TYP)
    index_totn_ref_typ = ref_matrix['totn']['typ'].index(TYP)
    index_totp_ref_typ = ref_matrix['totp']['typ'].index(TYP)
    
    if index_din_ref_typ != index_dip_ref_typ:
        print u'index för typ i DIN skiljer sig mot DIP'
    if index_din_ref_typ != index_totn_ref_typ:
        print u'index för typ i DIN skiljer sig mot Tot-N'
    if index_din_ref_typ != index_totp_ref_typ:
        print u'index för typ i DIN skiljer sig mot Tot-P'
    
    #months = "'11','12','01','02'"
    # MÅNADER ÄR SAMMA FÖR ALLA PARAMETRAR VINTER, (IAF ENLIGT DE GAMLA SCRIPTEN)
    months = unicode(ref_matrix['din']['month'][index_din_ref_typ])
    
    
    months_temp = months.replace("'","").split(',')
    months_int = np.array([])
    for mmm in months_temp:
        months_int = np.append(months_int,[int(mmm)],axis=0)
    
    #np.min(months_int[months_int>10])
    
    year_month_start = year_start + unicode(int(np.min(months_int[months_int>9])))
    
    year_month_end = unicode(int(year_end)+1) + unicode(int(np.max(months_int[months_int<5])))
    
    # eventuellt läsa in all data och sedan lägga in det i olika dictionaries..
    # tex Vinter = {'din':{station:[],date:[],serie:[],djup:[],value:[]},'totn':{}}
    
    
    
    # inlästa parametrar
    # statname,lat,lon,yr,mon,day,decd,sn,secchi,djp,t,s,o2,o2sat,dip,totp,no2,no3,nh4,totn,si
    
    
    keys = ['ctryid','shipid','station','latitude','longitude','year','month','day','hour','minute','bottom','serie','depth',\
        'temp','salt','Qsalt','o2','o2sat','po4','totp','no2','no3','nh4','nox','totn','sio4','chla']
        
    
    
    # Connect to the database
    #    cnxn = pyodbc.connect('DRIVER={Mimer};'
    #        'SERVER=Mimerprod01.smhi.se;DATABASE=lshark;'
    #        'UID=SHAAD;PWD=SHAAD') #autocommit=True för att utföra ändringar i databasen direkt
    
    # autocommit=True gör att ändringar genomförs direkt, tex behövs det om man ska skriva till databasen
    cnxn = pyodbc.connect(DRIVER = '{PostgreSQL Unicode}', server = 'postgresprod01',database = 'shark-int', uid = 'skint', pwd = 'Bvcdew21',  autocommit=True)
    
    cursor = cnxn.cursor()
    cursor.execute("""
        Select distinct 
    ctryid as "CtryID",
    shipid as "ShipID",
    stnreg.stnname as "Station",
    VISIT.latitud as "Lat", 
    VISIT.longitud as "Lon", 
    cast("year" as varchar) as "Year",
    "month" as "Month", 
    "day" as "Day",
    "hour" as "Hour",
    "minute" as "Minute",
    BOTTOMD as "Stationsdjup (m)",
    serie as "Serie", 
    cast(depth as Decimal(6,1)) as "Depth (m)", 
    CheckValidSharkValue(temp, qtemp) as "Temp (C)",
    (get_salt(salt,qsalt,ctdsalt,qctdsalt)).outvalue, 
    (get_salt(salt,qsalt,ctdsalt,qctdsalt)).outqflag,
    CheckValidSharkValue(calculateoxygen(O2, H2S, QH2S), QO2) as "O2 (ml/l)",
    CheckValidSharkValue(o2sat, qo2sat) as "O2sat",
    CheckValidSharkValue(po4, qpo4) as "PO4 (U+00B5mol/l)", 
    CheckValidSharkValue(totp, qtotp) as "TotP (U+00B5mol/l)", 
    CheckValidSharkValue(no2, qno2) as "NO2 (U+00B5mol/l)", 
    CheckValidSharkValue(no3, qno3) as "NO3 (U+00B5mol/l)", 
    CheckValidSharkValue(nh4, qnh4) as "NH4 (U+00B5mol/l)", 
    CheckValidSharkValue(nox, qnox) as "NOX (U+00B5mol/l)", 
    CheckValidSharkValue(totn, qtotn) as "TotN (U+00B5mol/l)", 
    CheckValidSharkValue(sio4, qsio4) as "SiO4 (U+00B5mol/l)",
    Cast(CheckValidSharkValueFloat(chla, qchla)as varchar(6)) as "Chla (U+00B5g/l)"
    from visit
    join stnreg using(sea1id, sea2id, sea3id, stnid)
    join depthtab using(serie, "year", ctryid, shipid)
    join hyddata using(serie, "year", ctryid, shipid, depthno )
    join biodata using(serie, "year", ctryid, shipid, depthno )
    join mastobs using(serie, "year", ctryid, shipid)
    join visproj using(serie, "year", ctryid, shipid)
    join visgroup using(serie, "year", ctryid, shipid)
    join groupreg using(grpid)
    where 1=1
    --and projid not like 'GUB' --denna ar med men som restricted i CDI, numera fri
    --and projid like 'GUB'
    and projid not like 'HES'
    --and projid not like 'NGV' and projid not like 'PBH' and projid not like 'PBV' -- detta endast 2011 Norrlands grunda vikar... kanske ska med anda senare.
    and Depth2 is null --For diskreta djup
    and "shipid" not in ('40')
    --AND "year" between '"""+year_start+"""' and '"""+year_end+"""'
    and "month" in ("""+months+""")
    and "year"||"month" > '"""+year_month_start+"""' -- tar bara slutet av 1997 som behovs for vinter
    and "year"||"month" < '"""+year_month_end+"""' -- tar bara borjan av 2013 som behovs for vinter 2012
    and depth <= cast('"""+depthlimit+"""' as float)
    
    and stnreg.stnname in ("""+stationslista+""")
    --and stnreg.stnname like 'ANHOLT E%'
    and (("ctryid" in ('77')) or (("year" >= '2011') and ("shipid" || '_' || "ctryid" || '_' || grpid) in ('01_26_OCLAB')) or (("year" >= '2014') and ("shipid" || '_' || "ctryid" || '_' || grpid) in ('01_34_OCLAB'))) -- Svenska baatar samt Dana >=2011 & Aranda >=2014 
    
    order by "Year", "Month", "Day", "Serie" """)
        #print x
    
    dbdata = cursor.fetchall()
    
    cursor.close()
    cnxn.close()
    
    if dbdata == []:
        print(u'\n!!! Ingen Data i denna typ (%s)!!!\n\nGaeller stationerna:\n' % TYP)
        for stat in stations_typ.keys():
            print(u'%s' % stat)
    
    
    data_matrix = {}
    for key in keys:
        data_matrix[key] = []
    
    
    # passa på att lägga på din..
    data_matrix['din'] = []
    
    stat_date = []
    date_list = []
    
    stat_temp = [] ####### tempkod
    test_list = []
    for row in dbdata:
        test_list.append(row)
        # kolla salt direkt
        if row[14] != '' and row[14] != None : # om salt saknas så spara inte data
        
            if row[2] not in stat_temp: ############# tempkod
                stat_temp.append(row[2]) ############ tempkod
            
            for col in range(len(row)):
                    
                if col == 14: # salt, kolla mot saltmax
                    
                    if float(row[col]) > ref_matrix['din']['saltmax'][index_din_ref_typ]: # samma saltmax för DIP, TotN, TotP
                        data_matrix[keys[col]].append(ref_matrix['din']['saltmax'][index_din_ref_typ])
                    elif row[col+1] == '<': # kolla om < flagga finns, ta då hälften av värdet. Borde bara finnas för salthalt = 2, det blir då 1.
                        data_matrix[keys[col]].append(float(row[col])/2.0)
                        print(u'Salthalt %s, har flagga "<", anvaend halva vaerdet: %s.  %s - %s' % (row[col],float(row[col])/2.0,row[2],row[5]+row[6]+row[7]))
                    else:
                        data_matrix[keys[col]].append(float(row[col]))
                elif keys[col] in ['po4','totn','totp']: # sätt float på po4, totn, totp
                    if row[col] != '' and row[col] != None:
                        data_matrix[keys[col]].append(float(row[col]))
                    else: # om värde saknas, skriv None
                        data_matrix[keys[col]].append(np.nan)
                else:
                    data_matrix[keys[col]].append(row[col])
            
            
            stat_date.append(row[2]+'_'+row[5]+row[6]+row[7])
            date_list.append(row[5]+row[6]+row[7])
            
            
            if data_matrix['nox'][-1] != '' and data_matrix['nox'][-1] != None:
                data_matrix['din'].append(float(data_matrix['nox'][-1]))
                
                if data_matrix['nh4'][-1] != '' and data_matrix['nh4'][-1] != None:
                    data_matrix['din'][-1] = data_matrix['din'][-1] + float(data_matrix['nh4'][-1])
                    
            elif data_matrix['no3'][-1] != '' and data_matrix['no3'][-1] != None:
                data_matrix['din'].append(float(data_matrix['no3'][-1]))
                
                if data_matrix['no2'][-1] != '' and data_matrix['no2'][-1] != None:
                    data_matrix['din'][-1] = data_matrix['din'][-1] + float(data_matrix['no2'][-1])
                if data_matrix['nh4'][-1] != '' and data_matrix['nh4'][-1] != None:
                    data_matrix['din'][-1] = data_matrix['din'][-1] + float(data_matrix['nh4'][-1])
            else:
                 data_matrix['din'].append(np.nan) # måste infoga np.nan om NO3 och NOX saknas, annars kan det bli för få poster.
            
            
    
    print stat_temp
    
    # ref_matrix['din']['saltmax'][index_ref_typ]
    
    #keys = ['ctryid','shipid','station','latitude','longitude','year','month','day','hour','minute','bottom','serie','depth',\
    #    'temp','salt','o2','o2sat','po4','totp','no2','no3','nh4','totn','sio4','chla']
    
    
    # ta bort data om salt saknas...  
    
    # o2sat > 100 ska uteslutas på västkusten... ('1n';'1s';'2';'3';'4';'5';'6';'25')
    
    # här ska medelvärden över djup skapas...
    
    # maxvärde för västkusten...
    
    
    # Calculate ref EK
    
    
    
    
    # # # EK = {'din':[],'dip':[],'totn':[],'totp':[]}
    s = np.array(data_matrix['salt'])
    
    
    # DIN
    ref_din = eval(ref_matrix['din']['ref'][index_din_ref_typ])
    ek_din=ref_din/(np.array(data_matrix['din']));
    
    # ersätt allt över 1 med 1
    index_1 = ek_din>1
    ek_din[index_1] = 1
    
    
    # DIP
    ref_dip = eval(ref_matrix['dip']['ref'][index_dip_ref_typ])
    ek_dip=ref_dip/(np.array(data_matrix['po4']));
    
    # ersätt allt över 1 med 1
    index_1 = ek_dip>1
    ek_dip[index_1] = 1
    
    
    # Tot-N
    ref_totn = eval(ref_matrix['totn']['ref'][index_totn_ref_typ])
    ek_totn=ref_totn/(np.array(data_matrix['totn']));
    
    # ersätt allt över 1 med 1
    index_1 = ek_totn>1
    ek_totn[index_1] = 1
    
    
    # Tot-P
    ref_totp = eval(ref_matrix['totp']['ref'][index_totp_ref_typ])
    ek_totp=ref_totp/(np.array(data_matrix['totp']));
    
    # ersätt allt över 1 med 1
    index_1 = ek_totp>1
    ek_totp[index_1] = 1
    
    
    
    # I västerhavet: (Gäller det bara Kväve?)
    # 1. först MEDEL EK från alla djupen (per provtagning)
    # 2. Sedan ta MAXvärdet (per säsong och station)
    
    # I övriga områden:
    # 1. först MEDEL EK från alla djupen (per provtagning)
    # 2. Sedan MEDEL av alla EK (från aktuell säsong och station)
    
    
    # year_start = '2010' # första året då data hämtas
    # year_end = '2011'
    
    # skapa en lista på alla år
    year_list = []
    year_list_str = []
    
    for y in range(int(year_end)+1-int(year_start)):
        year_list.append(int(year_start) + y)
        year_list_str.append(str(int(year_start) + y))
    
    
    #for y in range(int(year_end)-int(year_start)+1):
    #    year_list_str.append(str(int(year_start) + y))
    
    # keys = ['ctryid','shipid','station','latitude','longitude','year','month','day','hour','minute','bottom','serie','depth',\
    #     'temp','salt','o2','o2sat','po4','totp','no2','no3','nh4','totn','sio4','chla']
    
    stations = list(set(data_matrix['station']))
    
    # !!!
    # OBS, har gjort lite fel... högsta medelvärde på DIN används som mättillfälle
    # sedan tas alla data från bestämt mättillfälle och EK beräknas, sedan medelvärdesbildas det
    # !!!
    
    unik_meas = list(set(stat_date))
    
    unik_meas_stat = []
    unik_meas_date = []
    for i in range(len(unik_meas)):
        unik_meas_stat.append(unik_meas[i].split('_')[0])
        unik_meas_date.append(unik_meas[i].split('_')[1])
    
    
    # Dictionary med resultat
    #data_dict = {}
    
    data_dict_keys = ['typ','klass','EK','mean','std','antal_meas','provdatum','provtyp','provtyp_long','djup','values','provdatum_long','salthalt']
    # ['typ'], ['klass']  -  1 värde
    # ['EK'], ['medelvärde'], ['STD'], ['antal_mätningar'], ['provdatum'], ['provtyp']  -  1 värde per mättillfälle
    # ['djup'], ['värden'], ['provdatum_long'], ['salthalt']  -  flera värden per mättilfälle
    
    # loopa över station
    for stat in stations:
        
        if stat not in data_dict.keys():
            data_dict[stat] = {}
        
        index_stat = index_alla(data_matrix['station'],stat)
        
        unik_meas = list(set(stat_date))
        
        #np.array(data_matrix['year'])[index_stat]
        
        # loopa över alla säsonger(år):
        for y in year_list:
            
            # kolla om året saknas, lägg till i så fall
            if str(y) not in data_dict[stat].keys():
                data_dict[stat][str(y)] = {'din':{},'totn':{},'dip':{},'totp':{}} # data_dict[stat][year][para] klar
            
            # kolla även ifall någon enstaka parameter saknas, lägg till i så fall
            if 'din' not in data_dict[stat][str(y)].keys():
                data_dict[stat][str(y)]['din'] = {}
            
            if 'totn' not in data_dict[stat][str(y)].keys():
                data_dict[stat][str(y)]['totn'] = {}
            
            if 'dip' not in data_dict[stat][str(y)].keys():
                data_dict[stat][str(y)]['dip'] = {}
            
            if 'totp' not in data_dict[stat][str(y)].keys():
                data_dict[stat][str(y)]['totp'] = {}
            
            # data_dict_keys = ['typ','klass','EK','mean','std','antal_meas','provdatum','provtyp','djup','values','provdatum_long']
            
            # lägg till alla variabler
            for key in data_dict_keys:
                data_dict[stat][str(y)]['din'][key] = []
                data_dict[stat][str(y)]['totn'][key] = []
                data_dict[stat][str(y)]['dip'][key] = []
                data_dict[stat][str(y)]['totp'][key] = []
            # data_dict[stat][year][para] klar 
            
            months = ref_matrix['din']['month'][index_din_ref_typ].replace("'","").split(',')
            
            #antal_mattillfallen = 0
            
            index_season = []
            for m in months:
                if int(m)>10: #använd året
                    index_season = index_season + intersect(intersect(index_stat,index_alla(data_matrix['month'],m)),index_alla(data_matrix['year'],str(y)))
                    
                else: # använd nästkommande år
                    index_season = index_season + intersect(intersect(index_stat,index_alla(data_matrix['month'],m)),index_alla(data_matrix['year'],str(y+1)))
            
            din_season = {}
            totn_season = {}
            dip_season = {}
            totp_season = {}
            salt_season = {}
            date_season = []
            for ii in index_season:
                if (data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]) not in date_season:
                    date_season.append(data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii])
                
                if (data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]) not in din_season.keys():
                    din_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]] = []
                    totn_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]] = []
                    dip_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]] = []
                    totp_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]] = []
                    
                    salt_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]] = []
                
                din_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]].append(data_matrix['din'][ii])
                totn_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]].append(data_matrix['totn'][ii])
                dip_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]].append(data_matrix['po4'][ii])
                totp_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]].append(data_matrix['totp'][ii])
                salt_season[data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii]].append(data_matrix['salt'][ii])
                
                data_dict[stat][str(y)]['din']['djup'].append(data_matrix['depth'][ii])
                data_dict[stat][str(y)]['din']['values'].append(data_matrix['din'][ii])
                data_dict[stat][str(y)]['din']['provdatum_long'].append(data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii])
                data_dict[stat][str(y)]['din']['salthalt'].append(data_matrix['salt'][ii])
                data_dict[stat][str(y)]['din']['provtyp_long'].append('flaskprov')
                
                data_dict[stat][str(y)]['totn']['djup'].append(data_matrix['depth'][ii])
                data_dict[stat][str(y)]['totn']['values'].append(data_matrix['totn'][ii])
                data_dict[stat][str(y)]['totn']['provdatum_long'].append(data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii])
                data_dict[stat][str(y)]['totn']['salthalt'].append(data_matrix['salt'][ii])
                data_dict[stat][str(y)]['totn']['provtyp_long'].append('flaskprov')
                
                data_dict[stat][str(y)]['dip']['djup'].append(data_matrix['depth'][ii])
                data_dict[stat][str(y)]['dip']['values'].append(data_matrix['po4'][ii])
                data_dict[stat][str(y)]['dip']['provdatum_long'].append(data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii])
                data_dict[stat][str(y)]['dip']['salthalt'].append(data_matrix['salt'][ii])
                data_dict[stat][str(y)]['dip']['provtyp_long'].append('flaskprov')
                
                data_dict[stat][str(y)]['totp']['djup'].append(data_matrix['depth'][ii])
                data_dict[stat][str(y)]['totp']['values'].append(data_matrix['totp'][ii])
                data_dict[stat][str(y)]['totp']['provdatum_long'].append(data_matrix['year'][ii]+data_matrix['month'][ii]+data_matrix['day'][ii])
                data_dict[stat][str(y)]['totp']['salthalt'].append(data_matrix['salt'][ii])
                data_dict[stat][str(y)]['totp']['provtyp_long'].append('flaskprov')
                
                
                
            
            # OBS! denna är bara baserad på mättillfällen, har inte tagit hänsyn till om en parameter saknas, får nog kolla det också
            antal_mattillfallen = len(date_season)
            
            
            antal_mattillfallen_din = 0
            antal_mattillfallen_totn = 0
            antal_mattillfallen_dip = 0
            antal_mattillfallen_totp = 0
            for meas in date_season:
                
                for val_nr in range(len(din_season[meas])):
                    if ~np.isnan(din_season[meas][val_nr]) and ~np.isnan(salt_season[meas][val_nr]):
                        antal_mattillfallen_din += 1
                        break
                
                for val_nr in range(len(totn_season[meas])):
                    if ~np.isnan(totn_season[meas][val_nr]) and ~np.isnan(salt_season[meas][val_nr]):
                        antal_mattillfallen_totn += 1
                        break
                
                for val_nr in range(len(dip_season[meas])):
                    if ~np.isnan(dip_season[meas][val_nr]) and ~np.isnan(salt_season[meas][val_nr]):
                        antal_mattillfallen_dip += 1
                        break
                
                for val_nr in range(len(totp_season[meas])):
                    if ~np.isnan(totp_season[meas][val_nr]) and ~np.isnan(salt_season[meas][val_nr]):
                        antal_mattillfallen_totp += 1
                        break
            
            
            data_dict[stat][str(y)]['din']['antal_meas'] = antal_mattillfallen_din
            data_dict[stat][str(y)]['totn']['antal_meas'] = antal_mattillfallen_totn
            data_dict[stat][str(y)]['dip']['antal_meas'] = antal_mattillfallen_dip
            data_dict[stat][str(y)]['totp']['antal_meas'] = antal_mattillfallen_totp
            
            
            data_dict[stat][str(y)]['din']['typ'] = TYP
            data_dict[stat][str(y)]['totn']['typ'] = TYP
            data_dict[stat][str(y)]['dip']['typ'] = TYP
            data_dict[stat][str(y)]['totp']['typ'] = TYP
            
            
            
            
            if TYP in ['1n','1s','2','3','4','25','5','6']: # västerhavet, ta maxvärde
                if antal_mattillfallen >= min_antal_varden_vasterhavet: #ok, tillräckligt med mättillfällen
                    
                    # loopa över mättillfällen och ta ut tillfälle med max medelvärde
                    
                    #DIN & TOTN
                    if antal_mattillfallen_din >= min_antal_varden_vasterhavet:
                        din_max_mean = 0
                        
                        for meas in date_season:
                            din_mean_temp = np.mean(np.array(din_season[meas])[~np.isnan(np.array(din_season[meas]))])
                            
                            if din_mean_temp > din_max_mean:
                                din_max_mean = din_mean_temp
                                date_max_din = meas
                                
                                
                        data_dict[stat][str(y)]['din']['provdatum'] = [date_max_din]
                        data_dict[stat][str(y)]['totn']['provdatum'] = [date_max_din]
                        
                        data_dict[stat][str(y)]['din']['provtyp'] = 'flaskprov'
                        data_dict[stat][str(y)]['totn']['provtyp'] = 'flaskprov'
                        
                    else:
                        print(u'%s vinter %s/%s, för få mättillfällen för din (kan inte ta fram mätning med maxvärde), endast %s' % (stat,y,y+1,antal_mattillfallen_din))
                        
                        data_dict[stat][str(y)]['din']['EK'] = u'-'
                        #data_dict[stat][str(y)]['din']['mean'].append('-')
                        data_dict[stat][str(y)]['din']['std'] = u'-'
                        data_dict[stat][str(y)]['din']['provdatum'] = u'-'
                        data_dict[stat][str(y)]['din']['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)]['din']['klass'] = u'-'
                        
                        data_dict[stat][str(y)]['totn']['EK'] = u'-'
                        #data_dict[stat][str(y)]['totn']['mean'].append('-')
                        data_dict[stat][str(y)]['totn']['std'] = u'-'
                        data_dict[stat][str(y)]['totn']['provdatum'] = u'-'
                        data_dict[stat][str(y)]['totn']['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)]['totn']['klass'] = u'-'
                    
                    #DIP & TOTP
                    if antal_mattillfallen_dip >= min_antal_varden_vasterhavet: 
                        dip_max_mean = 0
                        
                        for meas in date_season:
                            dip_mean_temp = np.mean(np.array(dip_season[meas])[~np.isnan(np.array(dip_season[meas]))])
                            
                            if dip_mean_temp > dip_max_mean:
                                dip_max_mean = dip_mean_temp
                                date_max_dip = meas
                        
                        data_dict[stat][str(y)]['dip']['provdatum'] = [date_max_dip]
                        data_dict[stat][str(y)]['totp']['provdatum'] = [date_max_dip]
                        
                        data_dict[stat][str(y)]['dip']['provtyp'] = 'flaskprov'
                        data_dict[stat][str(y)]['totp']['provtyp'] = 'flaskprov'
                        
                    else:
                        print(u'%s vinter %s/%s, för få mättillfällen för dip (kan inte ta fram mätning med maxvärde), endast %s' % (stat,y,y+1,antal_mattillfallen_dip))
                        
                        data_dict[stat][str(y)]['dip']['EK'] = u'-'
                        #data_dict[stat][str(y)]['dip']['mean'].append('-')
                        data_dict[stat][str(y)]['dip']['std'] = u'-'
                        data_dict[stat][str(y)]['dip']['provdatum'] = u'-'
                        data_dict[stat][str(y)]['dip']['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)]['dip']['klass'] = u'-'
                        
                        data_dict[stat][str(y)]['totp']['EK'] = u'-'
                        #data_dict[stat][str(y)]['totp']['mean'].append('-')
                        data_dict[stat][str(y)]['totp']['std'] = u'-'
                        data_dict[stat][str(y)]['totp']['provdatum'] = u'-'
                        data_dict[stat][str(y)]['totp']['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)]['totp']['klass'] = u'-'
                    
                    
                    # DIN & TOTN
                    if antal_mattillfallen_din >= min_antal_varden_vasterhavet:
                        
                        s = np.array(salt_season[date_max_din])
                        nan_index_s = ~np.isnan(s)
                        
                        
                        ref_din = eval(ref_matrix['din']['ref'][index_din_ref_typ])
                        
                        nan_index_din = ~np.isnan(np.array(din_season[date_max_din]))
                        
                        if sum(nan_index_s & nan_index_din) < 2:
                            print(u'!!! Varning !!!\nEndast DIN-data användbart från %s djup' % sum(nan_index_s & nan_index_din))
                        
                        ek_din=ref_din[nan_index_s & nan_index_din]/(np.array(din_season[date_max_din])[nan_index_s & nan_index_din]);
                        
                        # ersätt allt över 1 med 1
                        index_1 = ek_din>1
                        ek_din[index_1] = 1
                        
                        
                        for ek_value in ek_din:
                            data_dict[stat][str(y)]['din']['EK'].append(ek_value)
                        
                        data_dict[stat][str(y)]['din']['std'] = np.std(np.array(din_season[date_max_din])[nan_index_s & nan_index_din])
                        
                        
                        # hög status
                        if np.mean(ek_din) > ref_matrix['din']['HG'][index_din_ref_typ]:
                            Nnedre = 4
                            EKovre = 1
                            EKnedre = ref_matrix['din']['HG'][index_din_ref_typ]
                        # god status
                        elif np.mean(ek_din) > ref_matrix['din']['GM'][index_din_ref_typ]:
                            Nnedre = 3
                            EKovre = ref_matrix['din']['HG'][index_din_ref_typ]
                            EKnedre = ref_matrix['din']['GM'][index_din_ref_typ]
                        # måttlig status
                        elif np.mean(ek_din) > ref_matrix['din']['MO'][index_din_ref_typ]:
                            Nnedre = 2
                            EKovre = ref_matrix['din']['GM'][index_din_ref_typ]
                            EKnedre = ref_matrix['din']['MO'][index_din_ref_typ]
                        # otillfredställande status
                        elif np.mean(ek_din) > ref_matrix['din']['OD'][index_din_ref_typ]:
                            Nnedre = 1
                            EKovre = ref_matrix['din']['MO'][index_din_ref_typ]
                            EKnedre = ref_matrix['din']['OD'][index_din_ref_typ]
                        # dålig status
                        else:
                            Nnedre = 0
                            EKovre = ref_matrix['din']['OD'][index_din_ref_typ]
                            EKnedre = 0
                        
                        Nklass_din = Nnedre + (np.mean(ek_din) - EKnedre)/(EKovre-EKnedre)
                        
                        data_dict[stat][str(y)]['din']['klass'] = Nklass_din
                        
                        print(u'%s vinter %s/%s: EK DIN = %s Klass = %s' % (stat,y,y+1,np.mean(ek_din),Nklass_din))
                        
                        # else:
                        # print(u'%s vinter %s/%s, för få mättillfällen för din, endast %s' % (stat,y,y+1,antal_mattillfallen_din))
                        
                        
                        # Tot-N
                        # if antal_mattillfallen_totn >= 3:
                        
                        ref_totn = eval(ref_matrix['totn']['ref'][index_totn_ref_typ])
                        
                        nan_index_totn = ~np.isnan(np.array(totn_season[date_max_din]))
                        
                        if sum(nan_index_s & nan_index_totn) < 2:
                            print(u'!!! Varning !!!\nEndast totN-data användbart från %s djup' % sum(nan_index_s & nan_index_totn))
                        
                        ek_totn=ref_totn[nan_index_s & nan_index_totn]/(np.array(totn_season[date_max_din])[nan_index_s & nan_index_totn]);
                        
                        # ersätt allt över 1 med 1
                        index_1 = ek_totn>1
                        ek_totn[index_1] = 1
                        
                        for ek_value in ek_totn:
                            data_dict[stat][str(y)]['totn']['EK'].append(ek_value)
                        
                        data_dict[stat][str(y)]['totn']['std'] = np.std(np.array(totn_season[date_max_din])[nan_index_s & nan_index_totn])
                        
                        
                        # hög status
                        if np.mean(ek_totn) > ref_matrix['totn']['HG'][index_totn_ref_typ]:
                            Nnedre = 4
                            EKovre = 1
                            EKnedre = ref_matrix['totn']['HG'][index_totn_ref_typ]
                        # god status
                        elif np.mean(ek_totn) > ref_matrix['totn']['GM'][index_totn_ref_typ]:
                            Nnedre = 3
                            EKovre = ref_matrix['totn']['HG'][index_totn_ref_typ]
                            EKnedre = ref_matrix['totn']['GM'][index_totn_ref_typ]
                        # måttlig status
                        elif np.mean(ek_totn) > ref_matrix['totn']['MO'][index_totn_ref_typ]:
                            Nnedre = 2
                            EKovre = ref_matrix['totn']['GM'][index_totn_ref_typ]
                            EKnedre = ref_matrix['totn']['MO'][index_totn_ref_typ]
                        # otillfredställande status
                        elif np.mean(ek_totn) > ref_matrix['totn']['OD'][index_totn_ref_typ]:
                            Nnedre = 1
                            EKovre = ref_matrix['totn']['MO'][index_totn_ref_typ]
                            EKnedre = ref_matrix['totn']['OD'][index_totn_ref_typ]
                        # dålig status
                        else:
                            Nnedre = 0
                            EKovre = ref_matrix['totn']['OD'][index_totn_ref_typ]
                            EKnedre = 0
                        
                        Nklass_totn = Nnedre + (np.mean(ek_totn) - EKnedre)/(EKovre-EKnedre)
                        
                        data_dict[stat][str(y)]['totn']['klass'] = Nklass_totn
                        
                        print(u'%s vinter %s/%s: EK totN = %s Klass = %s' % (stat,y,y+1,np.mean(ek_totn),Nklass_totn))
                        
                        # else:
                           # print(u'%s vinter %s/%s, för få mättillfällen för totN, endast %s' % (stat,y,y+1,antal_mattillfallen_totn))
                    
                    else:
                        # OBS! Denna kollen görs redan en gång tidigare, borde inte behövas igen, dock blir det inte fel eftersom jag bara lagrar '-' och inte appendar något
                        print(u'%s vinter %s/%s, för få mättillfällen för DIN, endast %s\n' % (stat,y,y+1,antal_mattillfallen_din))
                        print(u'Kan inte ta fram ett mättillfälle med högsta vinterpoolen av DIN')
                        
                        for para in ['din','totn']:
                            data_dict[stat][str(y)][para]['EK'] = u'-'
                            #data_dict[stat][str(y)][para]['mean'].append('-')
                            data_dict[stat][str(y)][para]['std'] = u'-'
                            data_dict[stat][str(y)][para]['provdatum'] = u'-'
                            data_dict[stat][str(y)][para]['provtyp'] = u'-'
                            
                            data_dict[stat][str(y)][para]['klass'] = u'-'
                    
                    
                    
                    # DIP & TOTP
                    if antal_mattillfallen_dip >= min_antal_varden_vasterhavet:
                        
                        s = np.array(salt_season[date_max_dip])
                        nan_index_s = ~np.isnan(s)
                        
                        
                        ref_dip = eval(ref_matrix['dip']['ref'][index_dip_ref_typ])
                        
                        nan_index_dip = ~np.isnan(np.array(dip_season[date_max_dip]))
                        
                        if sum(nan_index_s & nan_index_dip) < 2:
                            print(u'!!! Varning !!!\nEndast DIP-data användbart från %s djup' % sum(nan_index_s & nan_index_dip))
                        
                        ek_dip=ref_dip[nan_index_s & nan_index_dip]/(np.array(dip_season[date_max_dip])[nan_index_s & nan_index_dip]);
                        
                        # ersätt allt över 1 med 1
                        index_1 = ek_dip>1
                        ek_dip[index_1] = 1
                        
                        for ek_value in ek_dip:
                            data_dict[stat][str(y)]['dip']['EK'].append(ek_value)
                        
                        data_dict[stat][str(y)]['dip']['std'] = np.std(np.array(dip_season[date_max_dip])[nan_index_s & nan_index_dip])
                        
                        
                        # hög status
                        if np.mean(ek_dip) > ref_matrix['dip']['HG'][index_dip_ref_typ]:
                            Nnedre = 4
                            EKovre = 1
                            EKnedre = ref_matrix['dip']['HG'][index_dip_ref_typ]
                        # god status
                        elif np.mean(ek_dip) > ref_matrix['dip']['GM'][index_dip_ref_typ]:
                            Nnedre = 3
                            EKovre = ref_matrix['dip']['HG'][index_dip_ref_typ]
                            EKnedre = ref_matrix['dip']['GM'][index_dip_ref_typ]
                        # måttlig status
                        elif np.mean(ek_dip) > ref_matrix['dip']['MO'][index_dip_ref_typ]:
                            Nnedre = 2
                            EKovre = ref_matrix['dip']['GM'][index_dip_ref_typ]
                            EKnedre = ref_matrix['dip']['MO'][index_dip_ref_typ]
                        # otillfredställande status
                        elif np.mean(ek_dip) > ref_matrix['dip']['OD'][index_dip_ref_typ]:
                            Nnedre = 1
                            EKovre = ref_matrix['dip']['MO'][index_dip_ref_typ]
                            EKnedre = ref_matrix['dip']['OD'][index_dip_ref_typ]
                        # dålig status
                        else:
                            Nnedre = 0
                            EKovre = ref_matrix['dip']['OD'][index_dip_ref_typ]
                            EKnedre = 0
                        
                        Nklass_dip = Nnedre + (np.mean(ek_dip) - EKnedre)/(EKovre-EKnedre)
                        
                        data_dict[stat][str(y)]['dip']['klass'] = Nklass_dip
                        
                        print(u'%s vinter %s/%s: EK DIP = %s Klass = %s' % (stat,y,y+1,np.mean(ek_dip),Nklass_dip))
                        
                        # else:
                            # print(u'%s vinter %s/%s, för få mättillfällen för totN, endast %s' % (stat,y,y+1,antal_mattillfallen_dip))
                    
                        # Tot-P
                        # if antal_mattillfallen_totp >= 3:
                        
                        ref_totp = eval(ref_matrix['totp']['ref'][index_totp_ref_typ])
                        
                        nan_index_totp = ~np.isnan(np.array(totp_season[date_max_dip]))
                        
                        if sum(nan_index_s & nan_index_totp) < 2:
                            print(u'!!! Varning !!!\nEndast totP-data användbart från %s djup' % sum(nan_index_s & nan_index_totp))
                        
                        ek_totp=ref_totp[nan_index_s & nan_index_totp]/(np.array(totp_season[date_max_dip])[nan_index_s & nan_index_totp]);
                        
                        # ersätt allt över 1 med 1
                        index_1 = ek_totp>1
                        ek_totp[index_1] = 1
                        
                        for ek_value in ek_totp:
                            data_dict[stat][str(y)]['totp']['EK'].append(ek_value)
                        
                        data_dict[stat][str(y)]['totp']['std'] = np.std(np.array(totp_season[date_max_dip])[nan_index_s & nan_index_totp])
                        
                        
                        # hög status
                        if np.mean(ek_totp) > ref_matrix['totp']['HG'][index_totp_ref_typ]:
                            Nnedre = 4
                            EKovre = 1
                            EKnedre = ref_matrix['totp']['HG'][index_totp_ref_typ]
                        # god status
                        elif np.mean(ek_totp) > ref_matrix['totp']['GM'][index_totp_ref_typ]:
                            Nnedre = 3
                            EKovre = ref_matrix['totp']['HG'][index_totp_ref_typ]
                            EKnedre = ref_matrix['totp']['GM'][index_totp_ref_typ]
                        # måttlig status
                        elif np.mean(ek_totp) > ref_matrix['totp']['MO'][index_totp_ref_typ]:
                            Nnedre = 2
                            EKovre = ref_matrix['totp']['GM'][index_totp_ref_typ]
                            EKnedre = ref_matrix['totp']['MO'][index_totp_ref_typ]
                        # otillfredställande status
                        elif np.mean(ek_totp) > ref_matrix['totp']['OD'][index_totp_ref_typ]:
                            Nnedre = 1
                            EKovre = ref_matrix['totp']['MO'][index_totp_ref_typ]
                            EKnedre = ref_matrix['totp']['OD'][index_totp_ref_typ]
                        # dålig status
                        else:
                            Nnedre = 0
                            EKovre = ref_matrix['totp']['OD'][index_totp_ref_typ]
                            EKnedre = 0
                        
                        Nklass_totp = Nnedre + (np.mean(ek_totp) - EKnedre)/(EKovre-EKnedre)
                        
                        data_dict[stat][str(y)]['totp']['klass'] = Nklass_totp
                        
                        print(u'%s vinter %s/%s: EK totP = %s Klass = %s' % (stat,y,y+1,np.mean(ek_totp),Nklass_totp))
                        
                        # else:
                            # print(u'%s vinter %s/%s, för få mättillfällen för totN, endast %s' % (stat,y,y+1,antal_mattillfallen_totp))
                            
                    else:
                        # OBS! Denna kollen görs redan en gång tidigare, borde inte behövas igen, dock blir det inte fel eftersom jag bara lagrar '-' och inte appendar något
                        print(u'%s vinter %s/%s, för få mättillfällen för DIP, endast %s\n' % (stat,y,y+1,antal_mattillfallen_dip))
                        print(u'Kan inte ta fram ett mättillfälle med högsta vinterpoolen av DIP')
                        
                        for para in ['dip','totp']:
                            data_dict[stat][str(y)][para]['EK'] = u'-'
                            #data_dict[stat][str(y)][para]['mean'].append('-')
                            data_dict[stat][str(y)][para]['std'] = u'-'
                            data_dict[stat][str(y)][para]['provdatum'] = u'-'
                            data_dict[stat][str(y)][para]['provtyp'] = u'-'
                            
                            data_dict[stat][str(y)][para]['klass'] = u'-'
                    
                else:
                    print(u'%s vinter %s/%s, för få mättillfällen, endast %s, ingen parameter kan klassas' % (stat,y,y+1,antal_mattillfallen))
                    
                    for para in ['din','totn','dip','totp']:
                        data_dict[stat][str(y)][para]['EK'] = u'-'
                        #data_dict[stat][str(y)][para]['mean'].append('-')
                        data_dict[stat][str(y)][para]['std'] = u'-'
                        data_dict[stat][str(y)][para]['provdatum'] = u'-'
                        data_dict[stat][str(y)][para]['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)][para]['klass'] = u'-'
                    
                
            else: # ta medelvärde för på EK, EK beräknas för varje enskilt mätvärde
                if antal_mattillfallen >= min_antal_varden:
                    
                    
                    s = np.array(data_matrix['salt'])[index_season]
                    nan_index_s = ~np.isnan(s)
                    
                    #DIN
                    if antal_mattillfallen_din >= min_antal_varden:
                        
                        ref_din = eval(ref_matrix['din']['ref'][index_din_ref_typ])
                        
                        nan_index_din = ~np.isnan(np.array(data_matrix['din'])[index_season])
                        
                        if sum(nan_index_s & nan_index_din) < 2:
                            print(u'!!! Varning !!!\nEndast DIN-data användbart från %s djup' % sum(nan_index_s & nan_index_din))
                        
                        ek_din=ref_din[nan_index_s & nan_index_din]/((np.array(data_matrix['din'])[index_season])[nan_index_s & nan_index_din])
                        
                        # ersätt allt över 1 med 1
                        index_1 = ek_din>1
                        ek_din[index_1] = 1
                        
                        for ek_value in ek_din:
                            data_dict[stat][str(y)]['din']['EK'].append(ek_value)
                        
                        data_dict[stat][str(y)]['din']['std'] = np.std((np.array(data_matrix['din'])[index_season])[nan_index_s & nan_index_din])
                        
                        # Denna borde vara onödig eftersom jag använder 'provdatum_long' utanför västerhavet, skriver dessutom över denna med '-' nedan
                        # Dock ska jag nog kolla om 'provdatum_long' är helt korrekt.. tror den fyller på datum för ett besök för alla parametrar, även om värden för en parameter saknas
                        for dates_temp in set((np.array(date_list)[index_season])[nan_index_s & nan_index_din]):
                            data_dict[stat][str(y)]['din']['provdatum'].append(dates_temp)
                        
                        data_dict[stat][str(y)]['din']['provtyp'].append('flaskprov')
                        
                        # hög status
                        if np.mean(ek_din) > ref_matrix['din']['HG'][index_din_ref_typ]:
                            Nnedre = 4
                            EKovre = 1
                            EKnedre = ref_matrix['din']['HG'][index_din_ref_typ]
                        # god status
                        elif np.mean(ek_din) > ref_matrix['din']['GM'][index_din_ref_typ]:
                            Nnedre = 3
                            EKovre = ref_matrix['din']['HG'][index_din_ref_typ]
                            EKnedre = ref_matrix['din']['GM'][index_din_ref_typ]
                        # måttlig status
                        elif np.mean(ek_din) > ref_matrix['din']['MO'][index_din_ref_typ]:
                            Nnedre = 2
                            EKovre = ref_matrix['din']['GM'][index_din_ref_typ]
                            EKnedre = ref_matrix['din']['MO'][index_din_ref_typ]
                        # otillfredställande status
                        elif np.mean(ek_din) > ref_matrix['din']['OD'][index_din_ref_typ]:
                            Nnedre = 1
                            EKovre = ref_matrix['din']['MO'][index_din_ref_typ]
                            EKnedre = ref_matrix['din']['OD'][index_din_ref_typ]
                        # dålig status
                        else:
                            Nnedre = 0
                            EKovre = ref_matrix['din']['OD'][index_din_ref_typ]
                            EKnedre = 0
                        
                        Nklass_din = Nnedre + (np.mean(ek_din) - EKnedre)/(EKovre-EKnedre)
                        
                        data_dict[stat][str(y)]['din']['klass'] = Nklass_din
                        
                        print(u'%s vinter %s/%s: EK DIN = %s Klass = %s' % (stat,y,y+1,np.mean(ek_din),Nklass_din))
                        
                        # fyll i '-' på provdatum, används bara om ett prov används, som för västerhavet (använder 'provdatum_long' i denna functionen utanför västerhavet)
                        data_dict[stat][str(y)]['din']['provdatum'] = u'-'
                    
                    else:
                        print(u'%s vinter %s/%s, för få mättillfällen för DIN, endast %s av totalt %s mätningar' % (stat,y,y+1,antal_mattillfallen_din,antal_mattillfallen))
                        
                        data_dict[stat][str(y)]['din']['EK'] = u'-'
                        #data_dict[stat][str(y)]['din']['mean'].append('-')
                        data_dict[stat][str(y)]['din']['std'] = u'-'
                        data_dict[stat][str(y)]['din']['provdatum'] = u'-'
                        data_dict[stat][str(y)]['din']['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)]['din']['klass'] = u'-'
                    
                    
                    #Tot-N
                    if antal_mattillfallen_totn >= min_antal_varden:
                        
                        ref_totn = eval(ref_matrix['totn']['ref'][index_totn_ref_typ])
                        
                        nan_index_totn = ~np.isnan(np.array(data_matrix['totn'])[index_season])
                        
                        if sum(nan_index_s & nan_index_totn) < 2:
                            print(u'!!! Varning !!!\nEndast totN-data användbart från %s djup' % sum(nan_index_s & nan_index_totn))
                        
                        ek_totn=ref_totn[nan_index_s & nan_index_totn]/((np.array(data_matrix['totn'])[index_season])[nan_index_s & nan_index_totn]);
                        
                        # ersätt allt över 1 med 1
                        index_1 = ek_totn>1
                        ek_totn[index_1] = 1
                        
                        for ek_value in ek_totn:
                            data_dict[stat][str(y)]['totn']['EK'].append(ek_value)
                        
                        data_dict[stat][str(y)]['totn']['std'] = np.std((np.array(data_matrix['totn'])[index_season])[nan_index_s & nan_index_totn])
                        
                        # Denna borde vara onödig eftersom jag använder 'provdatum_long' utanför västerhavet, skriver dessutom över denna med '-' nedan
                        # Dock ska jag nog kolla om 'provdatum_long' är helt korrekt.. tror den fyller på datum för ett besök för alla parametrar, även om värden för en parameter saknas
                        for dates_temp in set((np.array(date_list)[index_season])[nan_index_s & nan_index_totn]):
                            data_dict[stat][str(y)]['totn']['provdatum'].append(dates_temp)
                        
                        data_dict[stat][str(y)]['totn']['provtyp'].append('flaskprov')
                        
                        # hög status
                        if np.mean(ek_totn) > ref_matrix['totn']['HG'][index_totn_ref_typ]:
                            Nnedre = 4
                            EKovre = 1
                            EKnedre = ref_matrix['totn']['HG'][index_totn_ref_typ]
                        # god status
                        elif np.mean(ek_totn) > ref_matrix['totn']['GM'][index_totn_ref_typ]:
                            Nnedre = 3
                            EKovre = ref_matrix['totn']['HG'][index_totn_ref_typ]
                            EKnedre = ref_matrix['totn']['GM'][index_totn_ref_typ]
                        # måttlig status
                        elif np.mean(ek_totn) > ref_matrix['totn']['MO'][index_totn_ref_typ]:
                            Nnedre = 2
                            EKovre = ref_matrix['totn']['GM'][index_totn_ref_typ]
                            EKnedre = ref_matrix['totn']['MO'][index_totn_ref_typ]
                        # otillfredställande status
                        elif np.mean(ek_totn) > ref_matrix['totn']['OD'][index_totn_ref_typ]:
                            Nnedre = 1
                            EKovre = ref_matrix['totn']['MO'][index_totn_ref_typ]
                            EKnedre = ref_matrix['totn']['OD'][index_totn_ref_typ]
                        # dålig status
                        else:
                            Nnedre = 0
                            EKovre = ref_matrix['totn']['OD'][index_totn_ref_typ]
                            EKnedre = 0
                        
                        Nklass_totn = Nnedre + (np.mean(ek_totn) - EKnedre)/(EKovre-EKnedre)
                        
                        data_dict[stat][str(y)]['totn']['klass'] = Nklass_totn
                        
                        print(u'%s vinter %s/%s: EK totN = %s Klass = %s' % (stat,y,y+1,np.mean(ek_totn),Nklass_totn))
                        
                        # fyll i '-' på provdatum, används bara om ett prov används, som för västerhavet (använder 'provdatum_long' i denna functionen utanför västerhavet)
                        data_dict[stat][str(y)]['totn']['provdatum'] = u'-'
                        
                    else:
                        print(u'%s vinter %s/%s, för få mättillfällen för totN, endast %s av totalt %s mätningar' % (stat,y,y+1,antal_mattillfallen_totn,antal_mattillfallen))
                        
                        data_dict[stat][str(y)]['totn']['EK'] = u'-'
                        #data_dict[stat][str(y)]['totn']['mean'].append('-')
                        data_dict[stat][str(y)]['totn']['std'] = u'-'
                        data_dict[stat][str(y)]['totn']['provdatum'] = u'-'
                        data_dict[stat][str(y)]['totn']['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)]['totn']['klass'] = u'-'
                    
                    #DIP
                    if antal_mattillfallen_dip >= min_antal_varden:
                        
                        ref_dip = eval(ref_matrix['dip']['ref'][index_dip_ref_typ])
                        
                        nan_index_dip = ~np.isnan(np.array(data_matrix['po4'])[index_season])
                        
                        if sum(nan_index_s & nan_index_dip) < 2:
                                print(u'!!! Varning !!!\nEndast DIP-data användbart från %s djup' % sum(nan_index_s & nan_index_dip))
                        
                        ek_dip=ref_dip[nan_index_s & nan_index_dip]/((np.array(data_matrix['po4'])[index_season])[nan_index_s & nan_index_dip])
                        
                        # ersätt allt över 1 med 1
                        index_1 = ek_dip>1
                        ek_dip[index_1] = 1
                        
                        for ek_value in ek_dip:
                            data_dict[stat][str(y)]['dip']['EK'].append(ek_value)
                        
                        data_dict[stat][str(y)]['dip']['std'] = np.std((np.array(data_matrix['po4'])[index_season])[nan_index_s & nan_index_dip])
                        
                        # Denna borde vara onödig eftersom jag använder 'provdatum_long' utanför västerhavet, skriver dessutom över denna med '-' nedan
                        # Dock ska jag nog kolla om 'provdatum_long' är helt korrekt.. tror den fyller på datum för ett besök för alla parametrar, även om värden för en parameter saknas
                        for dates_temp in set((np.array(date_list)[index_season])[nan_index_s & nan_index_dip]):
                            data_dict[stat][str(y)]['dip']['provdatum'].append(dates_temp)
                        
                        data_dict[stat][str(y)]['dip']['provtyp'].append('flaskprov')
                        
                        # hög status
                        if np.mean(ek_dip) > ref_matrix['dip']['HG'][index_dip_ref_typ]:
                            Nnedre = 4
                            EKovre = 1
                            EKnedre = ref_matrix['dip']['HG'][index_dip_ref_typ]
                        # god status
                        elif np.mean(ek_dip) > ref_matrix['dip']['GM'][index_dip_ref_typ]:
                            Nnedre = 3
                            EKovre = ref_matrix['dip']['HG'][index_dip_ref_typ]
                            EKnedre = ref_matrix['dip']['GM'][index_dip_ref_typ]
                        # måttlig status
                        elif np.mean(ek_dip) > ref_matrix['dip']['MO'][index_dip_ref_typ]:
                            Nnedre = 2
                            EKovre = ref_matrix['dip']['GM'][index_dip_ref_typ]
                            EKnedre = ref_matrix['dip']['MO'][index_dip_ref_typ]
                        # otillfredställande status
                        elif np.mean(ek_dip) > ref_matrix['dip']['OD'][index_dip_ref_typ]:
                            Nnedre = 1
                            EKovre = ref_matrix['dip']['MO'][index_dip_ref_typ]
                            EKnedre = ref_matrix['dip']['OD'][index_dip_ref_typ]
                        # dålig status
                        else:
                            Nnedre = 0
                            EKovre = ref_matrix['dip']['OD'][index_dip_ref_typ]
                            EKnedre = 0
                        
                        Nklass_dip = Nnedre + (np.mean(ek_dip) - EKnedre)/(EKovre-EKnedre)
                        
                        data_dict[stat][str(y)]['dip']['klass'] = Nklass_dip
                        
                        print(u'%s vinter %s/%s: EK DIP = %s Klass = %s' % (stat,y,y+1,np.mean(ek_dip),Nklass_dip))
                        
                        # fyll i '-' på provdatum, används bara om ett prov används, som för västerhavet (använder 'provdatum_long' i denna functionen utanför västerhavet)
                        data_dict[stat][str(y)]['dip']['provdatum'] = u'-'
                        
                    else:
                        print(u'%s vinter %s/%s, för få mättillfällen för DIP, endast %s av totalt %s mätningar' % (stat,y,y+1,antal_mattillfallen_dip,antal_mattillfallen))
                        
                        data_dict[stat][str(y)]['dip']['EK'] = u'-'
                        #data_dict[stat][str(y)]['dip']['mean'].append('-')
                        data_dict[stat][str(y)]['dip']['std'] = u'-'
                        data_dict[stat][str(y)]['dip']['provdatum'] = u'-'
                        data_dict[stat][str(y)]['dip']['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)]['dip']['klass'] = u'-'
                    
                    #Tot-P
                    if antal_mattillfallen_totp >= min_antal_varden:
                        
                        ref_totp = eval(ref_matrix['totp']['ref'][index_totp_ref_typ])
                        
                        nan_index_totp = ~np.isnan(np.array(data_matrix['totp'])[index_season])
                        
                        if sum(nan_index_s & nan_index_totp) < 2:
                                print(u'!!! Varning !!!\nEndast totP-data användbart från %s djup' % sum(nan_index_s & nan_index_totp))
                        
                        ek_totp=ref_totp[nan_index_s & nan_index_totp]/((np.array(data_matrix['totp'])[index_season])[nan_index_s & nan_index_totp]);
                        
                        # ersätt allt över 1 med 1
                        index_1 = ek_totp>1
                        ek_totp[index_1] = 1
                        
                        for ek_value in ek_totp:
                            data_dict[stat][str(y)]['totp']['EK'].append(ek_value)
                        
                        data_dict[stat][str(y)]['totp']['std'] = np.std((np.array(data_matrix['totp'])[index_season])[nan_index_s & nan_index_totp])
                        
                        # Denna borde vara onödig eftersom jag använder 'provdatum_long' utanför västerhavet, skriver dessutom över denna med '-' nedan
                        # Dock ska jag nog kolla om 'provdatum_long' är helt korrekt.. tror den fyller på datum för ett besök för alla parametrar, även om värden för en parameter saknas
                        for dates_temp in set((np.array(date_list)[index_season])[nan_index_s & nan_index_totp]):
                            data_dict[stat][str(y)]['totp']['provdatum'].append(dates_temp)
                        
                        data_dict[stat][str(y)]['totp']['provtyp'].append('flaskprov')
                        
                        # hög status
                        if np.mean(ek_totp) > ref_matrix['totp']['HG'][index_totp_ref_typ]:
                            Nnedre = 4
                            EKovre = 1
                            EKnedre = ref_matrix['totp']['HG'][index_totp_ref_typ]
                        # god status
                        elif np.mean(ek_totp) > ref_matrix['totp']['GM'][index_totp_ref_typ]:
                            Nnedre = 3
                            EKovre = ref_matrix['totp']['HG'][index_totp_ref_typ]
                            EKnedre = ref_matrix['totp']['GM'][index_totp_ref_typ]
                        # måttlig status
                        elif np.mean(ek_totp) > ref_matrix['totp']['MO'][index_totp_ref_typ]:
                            Nnedre = 2
                            EKovre = ref_matrix['totp']['GM'][index_totp_ref_typ]
                            EKnedre = ref_matrix['totp']['MO'][index_totp_ref_typ]
                        # otillfredställande status
                        elif np.mean(ek_totp) > ref_matrix['totp']['OD'][index_totp_ref_typ]:
                            Nnedre = 1
                            EKovre = ref_matrix['totp']['MO'][index_totp_ref_typ]
                            EKnedre = ref_matrix['totp']['OD'][index_totp_ref_typ]
                        # dålig status
                        else:
                            Nnedre = 0
                            EKovre = ref_matrix['totp']['OD'][index_totp_ref_typ]
                            EKnedre = 0
                        
                        Nklass_totp = Nnedre + (np.mean(ek_totp) - EKnedre)/(EKovre-EKnedre)
                        
                        data_dict[stat][str(y)]['totp']['klass'] = Nklass_totp
                        
                        print(u'%s vinter %s/%s: EK totP = %s Klass = %s' % (stat,y,y+1,np.mean(ek_totp),Nklass_totp))
                        
                        # fyll i '-' på provdatum, används bara om ett prov används, som för västerhavet (använder 'provdatum_long' i denna functionen utanför västerhavet)
                        data_dict[stat][str(y)]['totp']['provdatum'] = u'-'
                        
                    else:
                        print(u'%s vinter %s/%s, för få mättillfällen för totP, endast %s av totalt %s mätningar' % (stat,y,y+1,antal_mattillfallen_totp,antal_mattillfallen))
                        
                        data_dict[stat][str(y)]['totp']['EK'] = u'-'
                        #data_dict[stat][str(y)]['totp']['mean'].append('-')
                        data_dict[stat][str(y)]['totp']['std'] = u'-'
                        data_dict[stat][str(y)]['totp']['provdatum'] = u'-'
                        data_dict[stat][str(y)]['totp']['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)]['totp']['klass'] = u'-'
                    
                    #print(u'%s vinter %s/%s: EK din = %s' % (stat,y,y+1,np.mean(np.array(ek_din)[~np.isnan(np.array(ek_din))])))
                    #print(u'%s vinter %s/%s: EK totN = %s' % (stat,y,y+1,np.mean(np.array(ek_totn)[~np.isnan(np.array(ek_totn))])))
                    #print(u'%s vinter %s/%s: EK dip = %s' % (stat,y,y+1,np.mean(np.array(ek_dip)[~np.isnan(np.array(ek_dip))])))
                    #print(u'%s vinter %s/%s: EK totP = %s' % (stat,y,y+1,np.mean(np.array(ek_totp)[~np.isnan(np.array(ek_totp))])))
                    
                else:
                    print(u'%s vinter %s/%s, för få mättillfällen, endast %s, ingen parameter kan klassas' % (stat,y,y+1,antal_mattillfallen))
                    
                    for para in ['din','totn','dip','totp']:
                        data_dict[stat][str(y)][para]['EK'] = u'-'
                        #data_dict[stat][str(y)][para]['mean'].append('-')
                        data_dict[stat][str(y)][para]['std'] = u'-'
                        data_dict[stat][str(y)][para]['provdatum'] = u'-'
                        data_dict[stat][str(y)][para]['provtyp'] = u'-'
                        
                        data_dict[stat][str(y)][para]['klass'] = u'-'
    
    
    
    # data_dict klar
    
    return data_dict, test_list