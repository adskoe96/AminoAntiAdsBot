import webbrowser
import re
import aminofix

blacklisttg = {"@varebos"} #TELEGRAM CHANNELS THAT IN BLACKLIST
alreadySendedIds = [] #You don't have to delete it, this list is created so that the bot doesn't repeat the report of those people who HAVE sent ads, because it's pointless, right?
aminolinkpattern = r"aminoapps.com/p/\S+"
chatidForReports = "" #CHAT ID TO HAVE THE BOT SEND AD DETECTION
banreason = ["Amino Community Link", "Link to another Amino Community resource", "Telegram link", "Mentioning a blacklisted Telegram channel"] #REPORT MESSAGES
email = "" #BOT EMAIL
password = "" #BOT PASSWORD
methods = [] #USING FOR EVENTS
client = aminofix.Client()
print("Variables: Done")

try:
    client.login(email, password)
except aminofix.exceptions.VerificationRequired:
    print('Verification: ' + client.login(email=email, password=password)['url'])
    webbrowser.open(client.login(email=email, password=password)['url'])

print("Login Done: " + client.profile.nickname)
subclient = aminofix.SubClient(comId="Your Community Id", profile=client.profile)
print("SubClient: Done")

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
            SendMSG(cid=chatidForReports, msg=f"Ad Detection Report: {banreason[0]}\nAuthor: ndc://x{data.comId}/user-profile/{userid}")
            alreadySendedIds.append(userid)
        if 'aminoapps.com/p/' in content.lower() and userid != None and not userid in alreadySendedIds:
            link = extract_link(content.lower())
            if link:
                fullLink = "http://" + link
                bruhcomid = client.get_from_code(fullLink).comId
                if bruhcomid != data.comId:
                    SendMSG(cid=chatidForReports, msg=f"Ad Detection Report: {banreason[1]}\nAuthor: ndc://x{data.comId}/user-profile/{userid}")
                    alreadySendedIds.append(userid)
        if 't.me/' in content.lower() and userid != None and not userid in alreadySendedIds:
            SendMSG(cid=chatidForReports, msg=f"Ad Detection Report: {banreason[2]}\nAuthor: ndc://x{data.comId}/user-profile/{userid}")
            alreadySendedIds.append(userid)
        for word in blacklisttg:
            if word.lower() in content.lower() and userid != None and not userid in alreadySendedIds:
                SendMSG(cid=chatidForReports, msg=f"Ad Detection Report: {banreason[3]}\nAuthor: ndc://x{data.comId}/user-profile/{userid}")
                alreadySendedIds.append(userid)

for x in client.chat_methods:
    methods.append(client.event(client.chat_methods[x].__name__)(on_message))
