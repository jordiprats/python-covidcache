from flask import Flask, request

import re
import os
import sys
import time
import json
import requests

debug = True
covid_cache = {}

def fetch_status(id):
    global covid_cache
    try:
        if id in covid_cache.keys():
            if time.time()-covid_cache[id]['timestamp'] < 3600:
                if debug: print("cached data")
                return True
            else:
                if debug: print("updating scached data")
        
        # DATAGENERACIO;DATACREACIO;CODCENTRE;CODIMUNICIPI;ESTAT;GRUP_CONFIN;ALUMN_CONFIN;DOCENT_CONFIN;ALTRES_CONFIN;GRUP_ESTABLE;ALUMN_POSITIU;PERSONAL_POSITIU;ALTRES_POSITIU
        # 01/10/2020 7:00;28/09/2020 9:28;IDCENTRE;MUNICIPI;Obert;0;6;0;0;51;0;0;0
        # DATAGENERACIO;DATACREACIO;CODCENTRE;ESTAT;GRUP_CONFIN;ALUMN_CONFIN;DOCENT_CONFIN;ALTRES_CONFIN;GRUP_ESTABLE;ALUMN_POSITIU;PERSONAL_POSITIU;ALTRES_POSITIU
        # 03/10/2020 7:00;02/10/2020 8:51;IDCENTRE;Obert;0;5;0;0;51;0;0;0
        regex_str = '[0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+;([0-9]+)/([0-9]+)/[^;]+;'+id+';([^;]+);([0-9]+);([0-9]+);([0-9]+);([0-9]+);[0-9]+;([0-9]+);([0-9]+);([0-9]+)'
        if debug: print(regex_str)

        r = requests.get('https://tracacovid.akamaized.net/data.csv', stream=True)

        for line in r.iter_lines(decode_unicode=True):
            if debug: print(line)

            m = re.search(regex_str, line)
            if m:            
                ultim_update = (int(m.group(1))*100)+int(m.group(2))
                estat_centre = m.group(3)
                groups_confinats = int(m.group(4))
                confinats = int(m.group(5))+int(m.group(6))+int(m.group(7))
                positius = int(m.group(8))+int(m.group(9))+int(m.group(10))

                covid_cache[id] =   {
                                        'timestamp': time.time(),
                                        'ultim_update': ultim_update,
                                        'estat_centre': estat_centre,
                                        'groups_confinats': groups_confinats,
                                        'confinats': confinats,
                                        'positius': positius
                                    }

                return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        return False

app = Flask(__name__)

@app.route('/school/<id>')
def query_example(id):
    global covid_cache
    fetch_status(id)
    try:
        if covid_cache[id]:
            return json.dumps(covid_cache[id])
        else:
            return { 'WTF': True }
    except:
        pass
    return { 'WTF': True }

app.run(host='0.0.0.0', debug=debug, port=5000)