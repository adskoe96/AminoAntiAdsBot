import webbrowser
import re
import aminofix

blacklisttg = {"@varebos"} #ЧЕРНЫЙ СПИСОК ТЕЛЕГРАМ КАНАЛОВ
alreadySendedIds = [] #Удалять это не надо, этот список создан для того, чтобы бот не повторял отчет о тех людях, которые УЖЕ отправляли рекламу, ведь это бессмысленно, верно?
aminolinkpattern = r"aminoapps.com/p/\S+"
chatidForReports = "" #CHAT ID TO HAVE THE BOT SEND AD DETECTION
banreason = ["Ссылка на сообщество", "Ссылка на ресурс другого сообщества", "Ссылка на телеграм", "Упоминание телеграм канала из чёрного списка"] #СООБЩЕНИЯ РЕПОРТОВ
email = "" #ЭЛЕКТРОННАЯ ПОЧТА БОТА
password = "" #ПАРОЛЬ БОТА
methods = [] #ИСПОЛЬЗУЕТСЯ ДЛЯ ИВЕНТОВ
client = aminofix.Client()
print("Переменные готовы")

try:
    client.login(email, password)
except aminofix.exceptions.VerificationRequired:
    print('Требуется верификация: ' + client.login(email=email, password=password)['url'])
    webbrowser.open(client.login(email=email, password=password)['url'])

print("Логин завершен: " + client.profile.nickname)
subclient = aminofix.SubClient(comId="Your Community Id", profile=client.profile)
print("Клиент сообщества готов")

def SendMSG(cid: str, msg: str):
    subclient.send_message(chatId=cid, message=msg)

def extract_link(message: str):
    result = re.search(aminolinkpattern, message)
    if result:
        return result.group(0)

def on_message(data: aminofix.objects.Event):
    if data.message.author.userId != subclient.profile.userId:
        content = data.message.content
        if not content: content = "None"
        chatId = data.message.chatId
        nickname = data.message.author.nickname
        userid = data.message.author.userId
        title: str = client.get_community_info(data.comId).name
        print(title, chatId, nickname, content)
        if 'aminoapps.com/c/' in content.lower() and userid != None and not userid in alreadySendedIds:
            SendMSG(cid=chatidForReports, msg=f"Обнаружена реклама из разряда: {banreason[0]}\nАвтор: ndc://x{data.comId}/user-profile/{userid}")
            alreadySendedIds.append(userid)
        if 'aminoapps.com/p/' in content.lower() and userid != None and not userid in alreadySendedIds:
            link = extract_link(content.lower())
            if link:
                fullLink = "http://" + link
                bruhcomid = client.get_from_code(fullLink).comId
                if bruhcomid != data.comId:
                    SendMSG(cid=chatidForReports, msg=f"Обнаружена реклама из разряда: {banreason[1]}\nАвтор: ndc://x{data.comId}/user-profile/{userid}")
                    alreadySendedIds.append(userid)
        if 't.me/' in content.lower() and userid != None and not userid in alreadySendedIds:
            SendMSG(cid=chatidForReports, msg=f"Обнаружена реклама из разряда: {banreason[2]}\nАвтор: ndc://x{data.comId}/user-profile/{userid}")
            alreadySendedIds.append(userid)
        for word in blacklisttg:
            if word.lower() in content.lower() and userid != None and not userid in alreadySendedIds:
                SendMSG(cid=chatidForReports, msg=f"Обнаружена реклама из разряда: {banreason[3]}\nАвтор: ndc://x{data.comId}/user-profile/{userid}")
                alreadySendedIds.append(userid)

for x in client.chat_methods:
    methods.append(client.event(client.chat_methods[x].__name__)(on_message))
