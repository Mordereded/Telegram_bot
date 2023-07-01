
import time
from telebot import TeleBot, types
from re import findall, match
from requests import get, request
from bs4 import BeautifulSoup as bs
from pyowm import OWM
from pprint import pprint



bot = TeleBot('') #Необходимый токен телеграма
owmmm = OWM('beaa6a11f7555a5a2bca6267b8f83a08')
info = {
    'start': f'Привет!Я буду делится с вами курсом валют с сайта Investing. А так же вы можете узнать погоду, которая берется с сайта openweather\n\n'
             f'Отправьте /menu, чтобы попасть в меню. '
             f'Если хотите узнать доп информацию о возможных валютах то введите /help_currency',
    'open_markup': 'Меню',
    'currency' : 'Введите интересующую вас комбинацию валют в формате валюта-валюта. Ввод производится маленькими буквами латинского алфавита. Если хотите вывести все валюты то напишите all',
    'not_in_dict': 'Не знакомая команда. Попробуйте ввести  /menu',
    'prossesing' : 'Информация обрабатывается. Подождите пожалуйста',
    'error' : 'Ошибка. Вы ввели не корректное название валют.Попытайтесь ввести /currency снова!',
    'menu_back' : 'Для возвращения в главное мню напиишите /menu',
    'weather' : 'Выберите город в котором вы хотите узнать погоду'
 }
#Currency part 
def parse_currency_type(actual_date: str): #парсер 
    try:
        if((match(r'^[a-z]{3}[-][a-z]{3}', actual_date)) != None):
            real_date = match(r'^[a-z]{3}[-][a-z]{3}', actual_date).group()
        else: 
            return 'None'
    except TypeError:
        return 'None'
    else:
        new_date = real_date
        return new_date


def get_all_currency(message): # Получить информацию о всех валютах
    curr = 'https://ru.investing.com/currencies/streaming-forex-rates-majors'
    head = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
    full_page = get(curr,headers = head)
    soup = bs(full_page.content, 'html.parser')
    convert = soup.find_all('td', class_="bold left noWrap elp plusIconTd")
    curren = []
    newcurren = []
    for item in convert:
        curren.append(item.find('a').get_text())
    i = 0
    j = 0
    newline =''
    while ( i <len (curren)):
        while(j < 7):
            if(curren[i][j] == '/'):
                newline = newline + '-'
                j= j + 1 
            else:
                newline = newline +curren[i][j]
                j= j + 1
        newcurren.append(newline.lower())
        newline = ''
        i= i + 1
        j = 0

    all_currency = []
    for i in newcurren:
        url = f'https://ru.investing.com/currencies/{i}'
        if(i == 'btc-usd'):
            url = 'https://ru.investing.com/crypto/bitcoin/btc-usd'
        if(i == 'btc-eur'):
            url = 'https://ru.investing.com/crypto/bitcoin/btc-eur'
        if(i == 'eth-usd'):
            url = 'https://ru.investing.com/crypto/ethereum/eth-usd'
        head = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        full_page = get(url,headers = head)
        soup = bs(full_page.content, 'html.parser')
        price = soup.find_all("span", class_="text-2xl")
        name = soup.findAll("h1", {"class":"text-2xl font-semibold instrument-header_title__GTWDv mobile:mb-2"})
        all_currency.append('Курс ' + name[0].text + ' :' + price[0].text)
    newline = ''
    j = 0
    for i in all_currency:
        if(j % 4 == 0 ):
            newline = newline + '\n'
        else:
            newline = newline + i + ';   '
        j = j + 1 
    if len(newline) > 4096:
        for x in range(0, len(newline), 4096):
             bot.send_message(message.chat.id, newline[x:x+4096] )
    else:
        bot.send_message(message.chat.id, newline )
def get_currency(actual_currency: str): # Получить информацию о введенной валюте
    
    url = f'https://ru.investing.com/currencies/{actual_currency}'
    if(actual_currency =='btc-usd'):
        url = 'https://ru.investing.com/crypto/bitcoin/btc-usd'
    if(actual_currency == 'btc-eur'):
        url = 'https://ru.investing.com/crypto/bitcoin/btc-eur'
    if(actual_currency == 'eth-usd'):
        url = 'https://ru.investing.com/crypto/ethereum/eth-usd'
    head = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
    full_page = get(url,headers = head)
    soup = bs(full_page.content, 'html.parser')
    name = soup.findAll("h1", {"class":"text-2xl font-semibold instrument-header_title__GTWDv mobile:mb-2"})
    price = soup.findAll("span", {"class":"text-2xl"})
    return f'Курс {name[0].text} : {price[0].text}'


@bot.message_handler(commands=['start', 'help' ])
def start(message):
    bot.send_message(message.chat.id, info['start'])

@bot.message_handler(commands=['help_currency'])
def help(message):
    curr = 'https://ru.investing.com/currencies/streaming-forex-rates-majors'
    head = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
    full_page = get(curr,headers = head)
    soup = bs(full_page.content, 'html.parser')
    convert = soup.findAll("td", {"class":"bold left noWrap elp plusIconTd"}, )
    bot.send_message(message.chat.id, 'Возможные валюты')
    result = '|'
    for i in convert:
        for td in i.findAll("a"):
            result =  result +  td.text
            result = result + '|'  
    if len(result) > 4096:
        for x in range(0, len(result), 4096):
             bot.send_message(message.chat.id, result[x:x+4096] )
    else:
        bot.send_message(message.chat.id, result )



@bot.message_handler(commands=['menu'])
def currency(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    button_1 = types.KeyboardButton('Курсы валют 💰')
    button_2 = types.KeyboardButton('Погода ☀')
    markup.add(button_1, button_2)

    bot.send_message(message.chat.id, info['open_markup'], reply_markup=markup)


def answer_to_user(message):
    if(message.text == 'All' or message.text == 'all'):
        get_all_currency(message=message)
    else:

        parsed_date = parse_currency_type(actual_date=message.text)
    
        if(parsed_date != 'None'):
            bot.send_message(message.chat.id, get_currency(parsed_date))
            bot.send_message(message.chat.id, info('menu_back'))
        else:
            bot.send_message(message.chat.id, info('error'))


@bot.message_handler(content_types='text')
def reply(message):

    match message.text:
        case 'Курсы валют 💰':
            msg = bot.send_message(message.chat.id, info['currency'])
            bot.register_next_step_handler(msg,answer_to_user)
            bot.send_message(message.chat.id, 'Введите данные',reply_markup=types.ReplyKeyboardRemove())
        case 'Погода ☀':
            msg = bot.send_message(message.chat.id, info['weather'])
            bot.register_next_step_handler(msg,get_weather, city = msg, open_weather_token = owmmm )
            bot.send_message(message.chat.id, 'Ввод осуществляется латинскими букваим. Пример: Saint Petersburg' , reply_markup=types.ReplyKeyboardRemove())
        case 'Назад':  
            bot.send_message(message.chat.id, 'Выход', reply_markup=types.ReplyKeyboardRemove())
        case _:
            bot.send_message(message.chat.id, info['not_in_dict'])

### Weather part 
def get_weather(message,city, open_weather_token):
    bot.send_message(message.chat.id, '1')
    city = message.text
    bot.send_message(message.chat.id, '2')
    try:
        r = get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={'beaa6a11f7555a5a2bca6267b8f83a08'}&units=metric"
        )
        bot.send_message(message.chat.id, '3')
        data = r.json()
        pprint(data)
        city = data["name"]
        temp_max = data["main"]["temp_max"]
        temp = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        pressure = data['main']['pressure']
        sun_rise_time = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
        sun_set_time = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        bot.send_message(message.chat.id, f"Погода в городе :{city}\n"
                                          f"Температура: {temp}\n"
                                          f"Минимальная температура: {temp_min}С\n"
                                          f"Максимальная Температура: {temp_max}С\n"
                                          f"Давление: {pressure}мм.рт.ст\n"
                                          f"Время рассвета {sun_rise_time}\n"
                                          f"Время заката {sun_set_time}\n")
    except Exception as e:
        print(e)

if __name__ == '__main__': # чтобы код выполнялся только при запуске в виде сценария, а не при импорте модуля
    try:
       bot.polling(none_stop=True) # запуск бота
    except Exception as e:
       print(e) # или import traceback; traceback.print_exc() для печати полной инфы
       time.sleep(15)
