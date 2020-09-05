import folium as fl
from bs4 import BeautifulSoup
import requests
import time
import json
import branca.colormap as cm

url = 'https://index.minfin.com.ua/reference/coronavirus/ukraine/'
page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find('div', class_='sort1-table').find('div').find('table').findAll('tr')
data = {}
for i in range(1, len(table) - 1):
    city = table[i].contents[0].text
    infected = table[i].contents[1].text
    data[city] = infected
    time.sleep(0.05)


def get_city_name(x):
    return {
        u"Винницкая": 'Vinnytsya',
        u"Волынская": 'Volyn',
        u"Днепро­петровская": 'Dnipropetrovs\'k',
        u"Донецкая": 'Donets\'k',
        u"Житомирская": 'Zhytomyr',
        u"Закарпатская": 'Transcarpathia',
        u"Запорожская": 'Zaporizhzhya',
        u"Ивано-Франковская": 'Ivano-Frankivs\'k',
        u"Киевская": 'Kiev',
        u"Кирово­градская": 'Kirovohrad',
        u"Луганская": 'Luhans\'k',
        u"Львовская": 'L\'viv',
        u"Николаевская": 'Mykolayiv',
        u"Одесская": 'Odessa',
        u"Полтавская": 'Poltava',
        u"Ровенская": 'Rivne',
        u"Сумская": 'Sumy',
        u"Тернопольская": 'Ternopil\'',
        u"Харьковская": 'Kharkiv',
        u"Херсонская": 'Kherson',
        u"Хмельницкая": 'Khmel\'nyts\'kyy',
        u"Черкасская": 'Cherkasy',
        u"Черновицкая": 'Chernivtsi',
        u"Черниговская": 'Chernihiv',
        u"г.Киев": 'Kiev City'
    }.get(x, 'None')


with open("UA.geojson", 'r+', encoding='utf-8') as read_file:
    js = json.load(read_file)

    data_to_append = {}
    for city in data:
        latin_city = get_city_name(city)
        data_to_append[latin_city] = data[city]

    read_file.seek(0)
    for i in js['features']:
        city = i['properties']['name']
        if city in data_to_append:
            i['properties'].update({'infected': data_to_append[city]})
        else:
            i['properties'].update({'infected': 0})
    json.dump(js, read_file)
    read_file.truncate()

ua_map = fl.Map(location=[48.6992149, 31.2844733], zoom_start=7)
fg = fl.FeatureGroup(name='Ukraine COVID-19 map')

key_max = max([int(x) for x in data.values()])
key_min = min([int(x) for x in data.values()])
colormap = cm.linear.Reds_09.scale(key_min, key_max)

fg.add_child(fl.GeoJson(data=open('UA.geojson', 'r').read(),
                        popup=fl.GeoJsonPopup(fields=['name', 'infected'], aliases=['Region', 'Infected']),
                        style_function=lambda x: {'fillColor': colormap(int(x['properties']['infected'])), 'fillOpacity': 0.7},
                        highlight_function=lambda x: {'stroke': True, 'color': 'Blue', 'opacity': 0.2,
                                                      'fillOpacity': 1}))

ua_map.add_child(fg)
ua_map.add_child(fl.LayerControl())
ua_map.save('index.html')
