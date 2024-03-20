#bot_itog - version 1.2 - 16.04.2023
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from threading import Thread

################ Переменные #############
#      VK API переменные
token = "411f24e6a9226a28071d6ec578b1b38838f6cd6868aacdbaaf2aae247e66b5cad606fd9ee38ae22885e8a"
user_id = "212468291"
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)

#        Переменные Базы Данных
drugoy_cod = ''
local_cod = 0

#         Переменные путей
moonloader_put = 'E:/GTA TEST/moonloader/'

#         Переменные, хранящие чат
chat_new = [None]*4 #Массив, хранящий новые сообщения в чатах 4-ёх процессов гта
chat_old = [None]*4 #Массив, хранящий старые сообщения в чатах 4-ёх процессов гта. Он нужен, чтобы не флудить в бесконечном цикле бесконечным кол-вом сообщений
####################################################################################################

# Функция отправки сообщения в ВК
def otpravka(a):
    return (vk_session.get_api().messages.send(user_id=user_id, message=a, random_id=0))

def thread_function():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            msg = event.text
            if msg == 'помощь':
                otpravka('Это работает!!!')

thread1 = Thread(target=thread_function)
thread1.start()

# Стоп лист. Нужен, чтобы не флудить лишними сообщениями. Информацию о том, что лишнее берет из текстового файла
file = open("spisok.txt")
stop_list = file.readlines()
file.close()
for i in range (len(stop_list)):                  # Массив имеет в себе лишние символы '\n' из-за которых не работает распознование. В этом цикле они удаляются
    stop_list[i] = stop_list[i].replace('\n', '')


# Бесконечный цикл, делающий все действия на протяжении работы скрипта
while True:
     connection = pymysql.connect(                 # инициируем ссесию подключения к БД
         host="localhost",
         user="root",
         password="root",
         database="bot"
     )                                            # конец кода инициации подключения к БД

     with connection.cursor() as cursor:                                # из текущей сессии забираем значение кода ошибки
         cursor.execute('SELECT kod_oshibki FROM tablica')
         cod_oshibki_vrem = str(cursor.fetchall())                      # полученное из бд подобие массива превращаем в строку
         connection.close()                                             # закрываем ссесию
         cod_oshibki_vrem = cod_oshibki_vrem.split("(")                 # тут действия, которые удаляют всё лишнее и на выходе оставляют чистое число
         cod_oshibki_vrem = str(cod_oshibki_vrem[2])
         cod_oshibki_vrem = cod_oshibki_vrem.replace(',', '')
         cod_oshibki_vrem = cod_oshibki_vrem.replace(')', '')
         cod_oshibki = int(cod_oshibki_vrem)                            # конец действий, которые удаляют всё лишнее и на выходе оставляют чистое число

        # Отправка сообщений об ошибках
     if local_cod != cod_oshibki:
         local_cod = cod_oshibki
         if (cod_oshibki == 1) or (cod_oshibki == 2) or (cod_oshibki == 3) or (cod_oshibki == 4) or (cod_oshibki == 5):
             if cod_oshibki == 1:
                 otpravka('Проблемы c 1 gta')
             if cod_oshibki == 2:
                 otpravka('Проблемы c 2 gta')
             if cod_oshibki == 3:
                 otpravka('Проблемы c 3 gta')
             if cod_oshibki == 4:
                 otpravka('Проблемы c 4 gta')
             if cod_oshibki == 5:
                 otpravka('Проблемы c vpn')
         else:
             drugoy_cod = str(cod_oshibki)
             otpravka(('В БД что-то другое = ' + str(drugoy_cod)))


        # Работа с чатом
    for i in range (4):                           # цикл, запоминающий предыдущее значение переменной chat_new. Нужно для того, чтобы постоянно не флудить одним и тем же сообщением
        if chat_new[i] != None:                   # None нужно для того, чтобы при первом проходе, когда в переменной chat_new ничего нету, чтобы этот цикл не работал
            chat_old[i] = chat_new[i]

    for i in range(1,5):                          # в этом цикле открываем файлы и получаем новые значения перменной chat_new
        a = open((moonloader_put + str(i) + '.txt'),'r')
        chat_new[i-1] = a.read()
        a.close()

       # Отправка сообщений о чате, смене интерьеров и отсутствии аптечек
    for b in range(4):
        if chat_new[b] != chat_old[b]:            # в этом условии проверяем, если предыдущее значение переменной chat_new не равно текущему, то отправляем сообщение в вк. Это нужно, т.к. находимся в бесконечном цикле, чтобы не флудить бесконечно сообщениями

            if ("initiator:chat_obichniy" in chat_new[b]):     # если событие из чата, то...
                for i in range(len(stop_list)):                # для каждого слова из стоплиста
                    if stop_list[i] in chat_new[b]:            # если слово из стоплиста содержется в текущем файле, то не проверяем последующие слова, а делаем break из цикла со стоплиста. Тем самым переходим к следующему файлу
                        break
                    else:                                      # если текущее слово из стоплсита не содержется в файле
                        if i == (len(stop_list) - 1):          # и если текущее слово уже последнее в стоплисте, то отправляем сообщение в вк
                            otpravka(str('В гта ' + str(b+1) + ' было отправлено новое сообщение. Его текст: ' + (chat_new[b].replace('initiator:chat_obichniy ',''))))

            if ("initiator:smena_interyera" in chat_new[b]):
                otpravka(str('В гта ' + str(b + 1) + ' был изменен интерьер на ' + (chat_new[b].replace('initiator:smena_interyera ', ''))))

            if ("initiator:hp" in chat_new[b]):
                otpravka('В доме закончились аптечки. Инициатор - гта ' + str(b+1))

