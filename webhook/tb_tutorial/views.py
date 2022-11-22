from __future__ import print_function
import googleapiclient
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from django.shortcuts import render


import json
import os
import requests
from django.http import JsonResponse
from django.views import View

from tb_tutorial.models import *

import dokuwiki

import requests
from bs4 import BeautifulSoup
import sys
import json
import pickle
import os.path
import xmlrpc.client
import datetime
import csv
import subprocess
import re
import random
from urllib.parse import unquote

TELEGRAM_URL = "https://api.telegram.org/bot"
TUTORIAL_BOT_TOKEN = 'xxxxxxxxxxxxxxxxxxx'

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
# DOCUMENT_ID = '195j9eDD3ccgjQRttHhJPymLJUCOUjs-jmwTrekvdjFE'
# DOCUMENT_ID = '1qbioEIkxKVv1tRQouWtUXNAA-4pUhEMbBCnc9BtOV54'

admin_username = "AryanTR"
main_gp_ids = [-1001356415408, -1001424642902, -1001552491702] #-509360473,

wiki_username = 'telegrambot'
wiki_password = 'xxxxxx'
wiki_url = 'https://wiki.rastaiha.ir'

wiki = dokuwiki.DokuWiki(wiki_url, wiki_username, wiki_password)



# name_ids = {}

# emojies = {}
f = open('emojies.txt', 'r', encoding='UTF-8')
emojies = json.loads(f.read())
f.close()

edit_size = 200
score_coef = {
    'edit': 4,
    'import': 5,
    'seen': 2
}


def get_file_json(doc_id):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=doc_id).execute()
    return document


def get_title_str(document):
    return '======' + document.get('title') + '======\n'


def text_formatter(text):
    return text.translate(non_bmp_map).replace('\t', ' ')


def get_paragraph_element_str(element):
    if 'textRun' in element:
        x = text_formatter(element['textRun']['content']).strip().replace('//', '')
        if len(x.strip()) == 0:
            return ''
        if element['textRun']['textStyle'].get('bold'):
            x = '**' + x + '**'
        if 'link' in element['textRun']['textStyle']:
            x = '[[' + element['textRun']['textStyle']['link']['url'] + '|' + x + ']]'
        return '' + x + ''
    else:
        return ''


def get_bullet_prefix(document, list_id, nesting_level):
    bullet = document['lists'][list_id]['listProperties']['nestingLevels'][nesting_level]
    bullet_symbol = '-'
    if 'glyphSymbol' in bullet:
        bullet_symbol = '*'
    return ((nesting_level + 1) * 2) * ' ' + bullet_symbol + ' '


def get_structural_element_str(document, element):
    try:
        ss = ''
        for e in element['paragraph']['elements']:
            ss += get_paragraph_element_str(e)
        if len(ss.strip()) == 0:
            return ''
        if element['paragraph']['paragraphStyle'].get('namedStyleType') == 'HEADING_1':
            ss = '=====' + ss.strip() + '====='
        if element['paragraph']['paragraphStyle'].get('namedStyleType') == 'HEADING_2':
            ss = '====' + ss.strip() + '===='
        if element['paragraph']['paragraphStyle'].get('namedStyleType') == 'HEADING_3':
            ss = '===' + ss.strip() + '==='
        if element['paragraph']['paragraphStyle'].get('namedStyleType') == 'HEADING_4':
            ss = '==' + ss.strip() + '=='
        if element['paragraph']['paragraphStyle'].get('namedStyleType') == 'NORMAL_TEXT' and element['paragraph'][
            'paragraphStyle'].get('alignment') == 'JUSTIFIED' and 'bullet' not in element['paragraph']:
            ss = '###\n' + ss + '\n###\n'
        if 'bullet' in element['paragraph']:
            ss = '\n' + get_bullet_prefix(document, element['paragraph']['bullet']['listId'],
                                          element['paragraph']['bullet'].get('nestingLevel', 0)) + ss.strip()
        else:
            ss = '\n\n' + ss
        return ss
    except:
        return ''


def get_document_str(doc_id):
    document = get_file_json(doc_id)
    print('The title of the document is: {}'.format(document.get('title')))
    print(len(document['body']['content']))
    s = '{{page>الگو:نیازمند_تمیزکاری}}\n'
    s += '<WRAP center round info 60%>\n'
    s += 'لینک مرجع جهت تمیزکاری و تکمیل: [[https://docs.google.com/document/d/' + str(doc_id) + \
         '/edit?usp=sharing|این جا]]\n'
    s += '</WRAP>\n'
    s += get_title_str(document)
    for c in document['body']['content']:
        s += get_structural_element_str(document, c)
    return s


def name_to_id(name):
    if NameId.objects.filter(name__exact=name).count() > 0:
        return NameId.objects.filter(name__exact=name).all()[0].id
    n = NameId.objects.count()
    name_id = NameId.objects.create(name=name, id=n)
    name_id.save()
    return n


def id_to_name(idd):
    idd = int(idd)
    return NameId.objects.get(id__exact=idd).name


def normalize(text):
    res = text
    f = open('converter.txt', 'r', encoding='UTF-8')
    lines = [line.rstrip('\n') for line in f]
    for line in lines:
        l = line.split(',')
        res = res.replace(l[0], l[1] + ' ')
    return res


def anormalize(text):
    res = text
    f = open('converter.txt', 'r', encoding='UTF-8')
    lines = [line.rstrip('\n') for line in f]
    for line in lines:
        l = line.split(',')
        res = res.replace(l[1], l[0] + ' ')
    return res


def to_farsi(text):
    try:
        r = requests.post(
            'http://syavash.com/portal/modules/pinglish2farsi/convertor.php?lang=fa',
            data={
                'pinglish': text,
                'action': 'convert'
            }
        )
        soup = BeautifulSoup(r.text, 'html.parser')
        tags = soup.findAll('a')
        if len(tags) == 0 :
            return text
        p_text = ''
        for t in tags:
            p_text += t.string
        # p_text = soup.findAll('a')[0].string
        return p_text
    except:
        return text


def get_all_namespaces():
    d = {'': 0}
    all_pages = wiki.pages.list()
    for page in all_pages:
        l = page['id'].split(':')
        s = ''
        for i in range(len(l) - 1):
            if len(s) > 0:
                s += ':'
            s += l[i]
            d[s] = i + 1
    return d


def get_child_namespaces(namespaces_dic, namespace=''):
    l = []
    lvl = namespaces_dic[namespace]
    for n in namespaces_dic:
        if namespace in n:
            if namespaces_dic[n] == namespaces_dic[namespace] + 1:
                l.append(n)
    return l


def get_parent_namespace(namespace):
    l = namespace.split(':')
    s = ''
    for i in range(len(l) - 1):
        if len(s) > 0:
            s += ':'
        s += l[i]
    return s


def get_brother_namespace(namespace):
    res = []
    for page in wiki.pages.list(get_parent_namespace(namespace)):
        res.append(page['id'])
    return res


def compute_score(user):
    return score_coef['import'] * user.num_import + score_coef['edit'] * user.num_edit + score_coef[
        'seen'] * user.num_seen


def get_best(item):
    al = []
    for user in TlgUser.objects.all():
        al.append({
            'user': user,
            'edit': user.num_edit,
            'import': user.num_import,
            'seen': user.num_seen,
            'score': compute_score(user)
            })
    maxi = -1
    maxx = None
    for u in al:
        if u[item] > maxi:
            maxi = u[item]
            maxx = u['user']
    return maxx, maxi


class TutorialBotView(View):
    def post(self, request, *args, **kwargs):
        # self.send_message(request.body, 100581158)
        print(request.body)
        t_data = json.loads(request.body)
        if "message" in t_data:
            t_message = t_data["message"]
            t_chat = t_message["chat"]
            if "text" not in t_message:
                return JsonResponse({"ok": "POST request processed"})
            if t_chat["id"] in main_gp_ids:
                return JsonResponse({"ok": "POST request processed"})
            if t_message["text"] == "/start":
                self.start(t_message)
                return JsonResponse({"ok": "POST request processed"})
            if t_message["text"] == "/help":
                self.help(t_chat["id"])
            if t_message["text"] == "/sxp":
                self.sxp(t_chat["id"])

            tlg_id = t_message["from"]["id"]
            try:
                user = TlgUser.objects.filter(tlg_id__exact=tlg_id).all()[0]
            except:
                self.send_message('لطفا اول فرمان /start را بزنید.', t_chat["id"])
                return JsonResponse({"ok": "POST request processed"})

            if t_message["text"] == "/explore":
                self.explore(user, t_chat["id"])
            if t_message["text"] == "/get_state":
                self.get_state(user, t_chat["id"])
            if t_message["text"] == "/stat":
                self.stat(user, t_chat["id"])
            if t_message["text"] == "/hello":
                self.hello(user, t_chat["id"])
            if t_message["text"] == "/profile":
                self.profile(user, t_chat["id"])
            if t_message["text"] == "/reset":
                self.reset(user, t_chat["id"])
            if t_message["text"] == "/download":
                self.download(user, t_chat["id"])
            if t_message["text"] == "/import_google_doc":
                self.import_google_doc(user, t_chat["id"])
            if t_message["text"] == "/edit":
                self.get_edit(user, t_chat["id"])
            if t_message["text"] == "/cancel":
                self.reset(user, t_chat["id"])
            if t_message["text"] == "/next":
                self.get_edit(user, t_chat["id"])
            if t_message["text"] == "/save":
                self.save(user, t_chat["id"])
            if t_message["text"] == "/my_saves":
                self.my_saves(user, t_chat["id"])
            if t_message["text"] == "/leaderboard":
                self.leaderboard(user, t_chat["id"])
            if t_message["text"] == "/contents":
                self.download_contents(user, t_chat["id"])
# updater.dispatcher.add_handler(CommandHandler('send_messages', send_messages))

            if t_message["text"][0] != '/':
                self.text_parser(user, t_message["text"], t_chat["id"])
        if "callback_query" in t_data:
            tlg_id = t_data["callback_query"]["from"]["id"]
            try:
                user = TlgUser.objects.filter(tlg_id__exact=tlg_id).all()[0]
            except:
                self.send_message('لطفا اول فرمان /start را بزنید.', t_data["callback_query"]["message"]["chat"]["id"])
                return JsonResponse({"ok": "POST request processed"})
            self.callback_query_handler(user, t_data["callback_query"])
        # self.send_message('hello?', t_chat["id"])
        # self.send_message(request.body, 100581158)

        return JsonResponse({"ok": "POST request processed"})

    def callback_query_handler(self, user, callback_query):
        try:
            if 'help_' in callback_query['data']:
                id = int(callback_query['data'][5:])
                f = open('helps/help_' + str(id) + '.txt', 'r', encoding='UTF-8')
                text = f.read()
                f.close()
                f = open('helps/next_' + str(id) + '.txt', 'r', encoding='UTF-8')
                s = f.read()
                n = json.loads(s)
                f.close()
                x = []
                bef = []
                for i in range(len(n)):
                    if i % 2 == 0:
                        x.append(bef)
                        bef = []
                    bef.append({"text": n[i][0], "callback_data": 'help_' + str(n[i][1])})
                x.append(bef)
                self.edit_message(callback_query["message"]["message_id"],
                                  callback_query["message"]["chat"]["id"],
                                  text,
                                  reply_markup={"inline_keyboard": x}
                                  )

            if 'select_' in callback_query['data']:
                file_name = id_to_name(int(callback_query['data'][7:]))
                x = []
                x.append([{'text': emojies['download'] + 'دانلود',
                           'callback_data': 'download_' + str(name_to_id(file_name))}])
                x.append([{'text': emojies['link'] + 'لینک', 'callback_data': 'link_' + str(name_to_id(file_name))}])
                x.append([{'text': emojies['tag'] + 'ویرایش برچسب‌ها',
                           'callback_data': 'edittag_' + str(name_to_id(file_name))}])
                x.append([{'text': emojies['back'] + 'بازگشت',
                           'callback_data': 'explore_' + str(name_to_id(get_parent_namespace(file_name)))}])
                self.edit_message(callback_query["message"]["message_id"],
                                  callback_query["message"]["chat"]["id"],
                                  'شما در فايل <i>{}</i> هستيد.\nچه کنم؟:'.format(file_name),
                                  reply_markup={"inline_keyboard": x}
                                  )
            if 'explore_' in callback_query['data']:
                namespace = id_to_name(int(callback_query['data'][8:]))
                namespaces = get_child_namespaces(get_all_namespaces(), namespace)
                x = []
                for n in namespaces:
                    x.append([{'text': emojies['folder'] + n.split(':')[-1],
                               'callback_data': 'explore_' + str(name_to_id(n))}])
                files = wiki.pages.list(namespace)
                for file in files:
                    if get_parent_namespace(file['id']) != namespace:
                        continue
                    x.append([{'text': emojies['file'] + file['id'].split(':')[-1],
                               'callback_data': 'select_' + str(name_to_id(file['id']))}])

                x.append([{'text': emojies['import'] + 'ایجاد صفحه جدید',
                           'callback_data': 'import_' + str(name_to_id(namespace))}])
                x.append([{'text': emojies['back'] + 'بازگشت',
                           'callback_data': 'explore_' + str(name_to_id(get_parent_namespace(namespace)))}])
                self.edit_message(callback_query["message"]["message_id"],
                                  callback_query["message"]["chat"]["id"],
                                  'شما در فضاي <i>{}</i> هستيد.\nفضاها و فايل‌هاي زير موجود هستند:'.format(namespace),
                                  reply_markup={"inline_keyboard": x}
                                  )
            if 'link_' in callback_query['data']:
                file_name = id_to_name(int(callback_query['data'][5:]))
                self.edit_message(callback_query["message"]["message_id"],
                                  callback_query["message"]["chat"]["id"],
                                  '<a href="%s">%s</a>' %
                                  (wiki_url + '/doku.php/' + file_name.replace(':', '/'), file_name.split(':')[-1])
                                  )
            if 'import_' in callback_query['data']:
                file_name = id_to_name(int(callback_query['data'][7:]))
                user.cache = file_name
                user.state = States.get_page_name
                user.save()
                self.edit_message(callback_query["message"]["message_id"],
                                  callback_query["message"]["chat"]["id"],
                                  'چشم. اسم صفحه جدید چی باشه؟'
                                  )
            if 'edittag_' in callback_query['data']:
                file_name = id_to_name(int(callback_query['data'][8:]))
                user.state = 'edit_tags'
                user.save()
                # self.delete_message(callback_query["message"]["message_id"],
                #                     callback_query["message"]["chat"]["id"])
                self.send_suggested_tags(user, file_name, callback_query["message"]["chat"]["id"])
            if 'addtag_' in callback_query['data']:
                tag = id_to_name(int(callback_query['data'][7:]))
                tags = json.loads(user.cache1)
                user.num_edit += 1
                user.save()
                self.add_tag(user, user.cache, tag)
                real_tags = self.get_tags(user.cache)

                x = []
                bef = []
                for i in range(len(tags)):
                    if i % 2 == 0:
                        x.append(bef)
                        bef = []
                    if tags[i] in real_tags:
                        bef.append({"text": tags[i] + emojies["positive"],
                                    "callback_data": 'deletetag_' + str(name_to_id(tags[i]))})
                    else:
                        bef.append({"text": tags[i] + emojies["negative"],
                                    "callback_data": 'addtag_' + str(name_to_id(tags[i]))})
                x.append(bef)
                x.append([{"text": 'پایان' + emojies["finish"], "callback_data": 'finish'}])

                self.edit_message(callback_query["message"]["message_id"],
                                  callback_query["message"]["chat"]["id"],
                                  'ممنون.' + random.choice(emojies['thanks']) + ' لطفا در صورت صلاحدید بازهم اضافه کنید.',
                                  reply_markup={"inline_keyboard": x}
                                  )
            if 'deletetag_' in callback_query['data']:
                tag = id_to_name(int(callback_query['data'][10:]))
                tags = json.loads(user.cache1)
                user.num_edit += 1
                user.save()
                self.delete_tag(user, user.cache, tag)
                real_tags = self.get_tags(user.cache)

                x = []
                bef = []
                for i in range(len(tags)):
                    if i % 2 == 0:
                        x.append(bef)
                        bef = []
                    if tags[i] in real_tags:
                        bef.append({"text": tags[i] + emojies["positive"],
                                    "callback_data": 'deletetag_' + str(name_to_id(tags[i]))})
                    else:
                        bef.append({"text": tags[i] + emojies["negative"],
                                    "callback_data": 'addtag_' + str(name_to_id(tags[i]))})
                x.append(bef)
                x.append([{"text": 'پایان' + emojies["finish"], "callback_data": 'finish'}])

                self.edit_message(callback_query["message"]["message_id"],
                                  callback_query["message"]["chat"]["id"],
                                  'ممنون.' + random.choice(emojies['thanks']) + ' لطفا در صورت صلاحدید بازهم اضافه کنید.',
                                  reply_markup={"inline_keyboard": x}
                                  )
            if 'finish' in callback_query['data']:
                if user.state == 'edit_tags':
                    self.edit_message(callback_query["message"]["message_id"],
                                      callback_query["message"]["chat"]["id"],
                                      '<a href="{}">انجام شد.</a>'.format(wiki_url + '/doku.php/' +
                                                                          user.cache.replace(':', '/')),
                                      )
                    user.cache = ''
                    user.cache1 = ''
                    user.state = 'default'
                    user.save()
            if 'download_' in callback_query['data']:
                file_name = id_to_name(int(callback_query['data'][9:]))
                url = wiki_url + '/doku.php/'
                s = requests.Session()
                r = s.post(url, data={
                    'sectok': '',
                    'id': 'برگ آغازین',
                    'do': 'login',
                    'u': wiki_username,
                    'p': wiki_password
                })
                pdf_name = file_name.split(':')[-1] + '.pdf'
                url = url + file_name.replace(':', '/') + '?do=export_pdf'
                r = s.get(url, allow_redirects=True)
                open(pdf_name, 'wb').write(r.content)
                self.edit_message(callback_query["message"]["message_id"],
                                  callback_query["message"]["chat"]["id"],
                                  'بفرماین'
                                  )
                self.send_document(pdf_name, callback_query["message"]["chat"]["id"])
                # self.send_message(url, callback_query["message"]["chat"]["id"])
                # self.send_document(r.content, callback_query["message"]["chat"]["id"])
                # os.system('del ' + pdf_name)
                user.num_seen += 1
                user.save()
            if 'saved_' in callback_query['data']:
                id = int(callback_query['data'][6:])
                file = File.objects.filter(pk=id).all()[0]
                self.delete_message(
                    chat_id=callback_query['message']["chat"]["id"],
                    message_id=callback_query['message']['message_id']
                )
                self.send_message(
                    'متن زیر از صفحه‌ی <i>{}</i> انتخاب شده. لطفا به اینترها و دیگر علائم مخصوص دوکوویکی دست نزنید.'.format(file.page) +
                    'اگر از ادیت منصرف شدید دستور /cancel را بزنید و درصورتی که می‌خواهید صفحه‌ی دیگری را ادیت کنید /next را بزنید.' +
                    ' اگر قصد دارید این تکه از فایل را ذخیره کنید و بعدا آن را ویرایش کنید حتما دوباره دستور /save را بزنید.',
                    callback_query['message']["chat"]["id"])
                self.send_message(
                    # '`' + anormalize(file.text) + '`',
                    anormalize(file.text),
                    callback_query['message']["chat"]["id"]
                )
                user.state = States.edit
                user.cache = file.page
                user.cache1 = file.text
                user.save()
                file.delete()
        except Exception as e:
            # self.send_message(str(e), 100581158)
            print(str(e))
            self.send_message('مشکلي پيش آمده لطفا دستور را از ابتدا وارد کنيد.', callback_query['message']["chat"]["id"])

    def text_parser(self, user, text, chat_id):
        try:
            rules = [
                # (intiail_state, 'text_regex', func, 'next_state_true', 'next_state_false)
                (States.get_link, '\w+', self.download_link, States.default, States.default),
                (States.get_doc_id, '\w+', self.get_doc_id, States.edit_tags, States.get_doc_id),
                (States.get_address, '\w+', self.get_doc_address, States.get_doc_id, States.default),
                (States.get_page_name, '\w+', self.get_page_name, States.get_doc_id, States.default),
                (States.edit, '\w+', self.set_edit, States.default, States.default),
                (States.get_real_name, '\w+', self.realname, States.default, States.default),
                ('', 'اسم من «\w+»ه.', self.change_name, 'x', 'x'),
                # ('', '\w*عید\w*', congrat_eid, 'x', 'x')

            ]
            for rule in rules:
                if re.search(rule[0], user.state) is None:
                    continue
                if re.search(rule[1], text) is None:
                    continue
                if rule[2](user, text, chat_id):
                    if rule[3] != 'x':
                        user.state = rule[3]
                else:
                    if rule[4] != 'x':
                        user.state = rule[4]
                user.save()
                return
            self.send_message("شرمنده نمی‌فهمم چی می‌گین." + emojies['sad'], chat_id)
        except Exception as e:
            # self.send_message(str(e), 100581158)
            print(str(e))

    def help(self, chat_id):
        try:
            f = open('helps/help_0.txt', 'r', encoding='UTF-8')
            text = f.read()
            f.close()
            f = open('helps/next_0.txt', 'r', encoding='UTF-8')
            s = f.read()
            n = json.loads(s)
            f.close()
            x = []
            bef = []
            for i in range(len(n)):
                if i % 2 == 0:
                    x.append(bef)
                    bef = []
                bef.append({"text": n[i][0], "callback_data": 'help_' + str(n[i][1])})
            x.append(bef)
            self.send_message(text, chat_id, reply_markup={"inline_keyboard": x})
        except Exception as e:
            self.send_message(str(e), chat_id)

    def get_state(self, user, chat_id):
        try:
            self.send_message(user.state, chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def start(self, message):
        try:
            tlg_user = message["from"]
            chat_id = message["chat"]["id"]

            verified = False
            for main_gp_id in main_gp_ids:
                try:
                    data = {
                        'chat_id': main_gp_id,
                        'user_id': tlg_user["id"]
                    }
                    r = requests.post(f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/getChatMember", data=data)
                    # self.send_message(r.text, 100581158)
                    j = json.loads(r.text)
                    if j['result']['status'] in ['creator', 'administrator', 'member', 'restricted']:
                        verified = True
                except:
                    pass
            if not verified:
                self.send_message(
                    'متاسفانه هویت رستایی شما تایید نشد. اگر عضو گروه خانواده هستید و این پیام را دریافت کرده‌اید به ادمین پیام دهید.',
                    chat_id
                )
                return

            if TlgUser.objects.filter(tlg_id__exact=tlg_user["id"]).count():
                self.send_message('استاد اين‌قدر استارت نزن ناموسا:)))', chat_id)
                return
            if "first_name" not in tlg_user:
                tlg_user["first_name"] = ''
            if "last_name" not in tlg_user:
                tlg_user["last_name"] = ''
            if "username" not in tlg_user:
                tlg_user["username"] = ''
            user = TlgUser.objects.create(
                username=tlg_user["username"],
                first_name=tlg_user["first_name"],
                last_name=tlg_user["last_name"],
                tlg_id=tlg_user["id"],
                state=States.get_real_name,
                persian_name=to_farsi(tlg_user["first_name"]),
                real_name=tlg_user["first_name"] + ' ' + tlg_user["last_name"],
                cache='',
                cache1='',
                num_seen=0,
                num_import=0,
                num_edit=0
            )
            user.save()
            self.send_message('سلام {}!'.format(user.persian_name), chat_id)
            self.send_message('به‌به خوش اومدين!', chat_id)
            self.send_message('در ابتدا لطفا نام کامل خود را وارد بفرمایید.', chat_id)
        except Exception as e:
            self.send_message(str(e), message["chat"]["id"])

    def sxp(self, chat_id):
        self.send_message('حقيقتا سطح!', chat_id)

    def explore(self, user, chat_id):
        try:
            s = 'فضاها و فايل‌هاي زير موجود هستند:\n'
            x = []
            namespaces = get_child_namespaces(get_all_namespaces())
            for namespace in namespaces:
                x.append([{'text': emojies['folder'] + namespace,
                           'callback_data':'explore_' + str(name_to_id(namespace))}])
            self.send_message(s, chat_id, reply_markup={'inline_keyboard': x})
        except Exception as e:
            self.send_message(str(e), chat_id)

    def stat(self, user, chat_id):
        try:
            if user.username != admin_username:
                return
            for user in TlgUser.objects.all():
                self.send_message(user.persian_name + ' به آيدي @' + user.username + ' با ' +
                                  str(user.num_seen) + ':' + str(user.num_import) + ':' + str(user.num_edit),
                                  chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def hello(self, user, chat_id):
        try:
            name = user.persian_name
            self.send_message('سلام {}!'.format(name), chat_id)
            # if 6 <= datetime.datetime.now().hour < 12:
            #     update.message.reply_text(
            #         'صبح شما بخير!')
        except Exception as e:
            self.send_message(str(e), chat_id)

    def reset(self, user, chat_id):
        try:
            user.state = States.default
            user.save()
            self.send_message('انجام شد.', chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def profile(self, user, chat_id):
        try:
            self.send_message(
                'شما دارای %d ادیت(%s)، %d وارد کردن(%s) و %d دانلود سند(%s) هستید.\nامتیاز شما در مجموع %d(%s) است.' %
                (user.num_edit, emojies['edit'], user.num_import, emojies['import'], user.num_seen, emojies['seen'],
                 compute_score(user), emojies['star']), chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def download(self, user, chat_id):
        try:
            user.state = States.get_link
            user.save()
            self.send_message('بسيار هم خوب. لطفا لينک مورد نظر رو بفرستين.', chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def import_google_doc(self, user, chat_id):
        try:
            user.state = States.get_address
            user.save()
            self.send_message('عالی! حال آدرس مورد نظر را وارد کنید.', chat_id)
            # self.send_message('بسيار هم خوب. لطفا آیدی یا لینک مورد نظر را وارد کنید.', chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def leaderboard(self, user, chat_id):
        try:
            s = ''
            user, num = get_best('seen')
            s += 'بیش‌ترین تعداد دانلود(%s) در اختیار <b>%s</b> است با دیدن %d صفحه\n\n' % (
                emojies['seen'], user.real_name, num)

            user, num = get_best('edit')
            s += 'بیش‌ترین تعداد ویرایش(%s) در اختیار <b>%s</b> است با ویرایش %d صفحه\n\n' % (
                emojies['edit'], user.real_name, num)

            user, num = get_best('import')
            s += 'بیش‌ترین تعداد وارد کردن(%s) در اختیار <b>%s</b> است با وارد کردن %d صفحه\n\n' % (
                emojies['import'], user.real_name, num)

            user, num = get_best('score')
            s += 'بیش‌ترین امتیاز کل(%s) در اختیار <b>%s</b> است با %d امتیاز\n\n' % (
                emojies['star'], user.real_name, num)

            self.send_message(s, chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def get_edit(self, user, chat_id):
        try:
            all_pages = wiki.pages.list()
            page = random.choice(all_pages)['id']
            content = wiki.pages.get(page)
            start = random.randint(0, len(content) - 1)
            while content[start] != '\n' and start > 0:
                start -= 1
            end = start + edit_size
            if end > len(content):
                end = len(content)
            while content[end - 1] != '\n' and end < len(content):
                end += 1
            chunk = content[start:end].strip()

            user.state = States.edit
            user.cache = page
            user.cache1 = chunk
            user.save()

            self.send_message(
                'متن زیر از صفحه‌ی <i>{}</i> انتخاب شده. لطفا به اینترها و دیگر علائم مخصوص دوکوویکی دست نزنید.'.format(
                    page) +
                'اگر از ادیت منصرف شدید دستور /cancel را بزنید و درصورتی که می‌خواهید صفحه‌ی دیگری را ادیت کنید /next را بزنید.' +
                ' اگر قصد دارید این تکه از فایل را ذخیره کنید و بعدا آن را ویرایش کنید دستور /save را بزنید.',
                chat_id)
            # update.message.reply_text(anormalize(chunk), parse_mode=telegram.ParseMode.MARKDOWN_V2)
            self.send_message(anormalize(chunk), chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def save(self, user, chat_id):
        try:
            if user.state != States.edit:
                return
            file = File.objects.create(
                page=user.cache,
                user=user,
                text=user.cache1
            )
            file.save()
            user.cache = ''
            user.cache1 = ''
            user.state = States.default
            user.save()
            self.send_message('ذخیره شد. حالا چه خدمتی از دست‌ام ساخته‌ست؟', chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def my_saves(self, user, chat_id):
        try:
            s = 'شما تکه فایل‌های زیر را جهت ویرایش ذخیره کرده‌اید:\n'
            x = []
            for file in user.files.all():
                x.append([{'text': emojies['file'] + file.page, 'callback_data': 'saved_' + str(file.pk)}])
            if len(x) > 0:
                self.send_message(s, chat_id, reply_markup={'inline_keyboard': x})
            else:
                self.send_message('شما در حال حاضر هیچ تکه فایلی برای ویرایش ذخیره نکرده‌اید.' + emojies['sad'], chat_id)
        except Exception as e:
            self.send_message(str(e), chat_id)

    def download_contents(self, user, chat_id):
        try:
            url = wiki_url + '/doku.php/'
            s = requests.Session()
            r = s.post(url, data={
                'sectok': '',
                'id': 'برگ آغازین',
                'do': 'login',
                'u': wiki_username,
                'p': wiki_password
            })
            pdf_name = 'فهرست' + '.pdf'
            url = 'https://wiki.rastaiha.ir/doku.php/%D9%88%DB%8C%DA%A9%DB%8C/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%B5%D9%81%D8%AD%D9%87_%D9%87%D8%A7?do=export_pdf'
            r = s.get(url, allow_redirects=True)
            open(pdf_name, 'wb').write(r.content)
            self.send_document(pdf_name, chat_id)
            user.num_seen += 1
            user.save()
        except Exception as e:
            self.send_message(str(e), chat_id)

    # text commands functions
    def change_name(self, user, text, chat_id):
        name = re.search(r'«(\w+)»', text).group(1)
        if user.persian_name == name:
            self.send_message('خب من هم که همينو گفته بودم!', chat_id)
            return False
        user.persian_name = name
        user.save()
        self.send_message('شرمنده {}، نتونسته بودم اسم‌تو درست بخونم.'.format(user.persian_name), chat_id)
        return True

    def realname(self, user, text, chat_id):
        user.real_name = text
        user.save()
        self.send_message('حل‌ه.', chat_id)
        self.send_message('آیا مایلید از نحوه‌ی کار با بات اطلاع یابید؟ دستور /help را وارد کنید.', chat_id)
        return True

    def download_link(self, user, text, chat_id):
        url = wiki_url + '/doku.php/'
        s = requests.Session()
        r = s.post(url, data={
            'sectok': '',
            'id': 'برگ آغازین',
            'do': 'login',
            'u': wiki_username,
            'p': wiki_password
        })
        pdf_name = unquote(text.split('/')[-1]) + '.pdf'
        url = text + '?do=export_pdf'
        r = s.get(url, allow_redirects=True)
        open(pdf_name, 'wb').write(r.content)
        self.send_document(pdf_name, chat_id)
        user.num_seen += 1
        user.save()
        return True

    def get_doc_id(self, user, text, chat_id):
        try:
            new_content = get_document_str(text)
        except googleapiclient.errors.HttpError:
            try:
                id = re.search(r'docs.google.com/document/d/(\S+)/edit', text).group(1)
                new_content = get_document_str(id)
            except:
                self.send_message(
                    'شرمنده‌ام ولی فکر کنم آیدی درستی وارد نکرده‌اید. اگر از آیدی مطمئن لطفا هستید دسترسی‌های داک را بررسی فرمایید'
                    + ' و دوباره آیدی درست را وارد کنید.'
                    + emojies["sad"], chat_id)
                return False
        wiki.pages.set(user.cache, new_content, sum='به دستور ' + user.real_name + ' از گوگل داک وارد شد')
        user.num_import += 1
        user.save()
        self.send_suggested_tags(user, user.cache, chat_id)
        return True

    def get_doc_address(self, user, text, chat_id):
        user.cache = text
        user.save()
        self.send_message('بسيار هم خوب. لطفا آیدی یا لینک مورد نظر را وارد کنید.', chat_id)
        return True

    def get_page_name(self, user, text, chat_id):
        user.cache = user.cache + ':' + text
        user.save()
        self.send_message('بسيار هم خوب. لطفا آیدی یا لینک مورد نظر را وارد کنید.', chat_id)
        return True

    def set_edit(self, user, text, chat_id):
        content = wiki.pages.get(user.cache)
        new_content = content.replace(user.cache1, normalize(text))
        wiki.pages.set(user.cache, new_content, sum='به دستور ' + user.real_name + ' ویرایش شد')
        user.cache = ''
        user.cache1 = ''
        user.num_edit += 1
        user.save()
        self.send_message(
            'ممنون.' + random.choice(emojies['thanks']),
            chat_id
        )
        return True

    # wiki functions
    def delete_tag(self, user, wiki_address, tag):
        content = wiki.pages.get(wiki_address)
        tags = re.search(r"{{\s*tag>(\w|\s)*}}", content).group(0)
        if tag not in tags:
            return
        new_tags = tags.replace(tag, '')
        new_content = content.replace(tags, new_tags)
        wiki.pages.set(wiki_address, new_content, sum='به دستور ' + user.real_name + ' تگ‌ها ویرایش شد', minor=True)

    def add_tag(self, user, wiki_address, tag):
        content = wiki.pages.get(wiki_address)
        try:
            tags = re.search(r"{{\s*tag>(\w|\s)*}}", content).group(0)
            if tag in self.get_tags(wiki_address):
                return
            new_tags = tags.replace('}}', ' ' + tag + ' }}')
            new_content = content.replace(tags, new_tags)
        except:
            new_content = content + '\n\n{{tag> ' + tag + ' }}'
        wiki.pages.set(wiki_address, new_content, sum='به دستور ' + user.real_name + ' تگ‌ها ویرایش شد', minor=True)

    def get_tags(self, wiki_address):
        try:
            content = wiki.pages.get(wiki_address)
            tags = re.search(r"{{\s*tag>((\w|\s)*)}}", content).group(1)
            return tags.strip().split(' ')
        except:
            return []

    def get_all_tags(self):
        url = wiki_url + '/doku.php/'
        s = requests.Session()
        r = s.post(url, data={
            'sectok': '',
            'id': 'برگ آغازین',
            'do': 'login',
            'u': wiki_username,
            'p': wiki_password
        })
        url = 'https://wiki.rastaiha.ir/doku.php/%D9%88%DB%8C%DA%A9%DB%8C/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%A8%D8%B1%DA%86%D8%B3%D8%A8_%D9%87%D8%A7'
        r = s.get(url, allow_redirects=True)
        soup = BeautifulSoup(r.text, 'html.parser')
        tags = soup.select('.cloud a')
        res = []
        for t in tags:
            res.append(t.string)
        return res

    def send_suggested_tags(self, user, text, chat_id):
        message = self.send_message(
            'اندکی صبر سحر نزدیک است. کارگران ویکی‌یار ' + emojies["workers"] + ' در حال بررسی درخواست شما هستند.',
            chat_id
        )

        dic_tags = {}
        brothers = get_brother_namespace(text)
        for b in brothers:
            tags = self.get_tags(b)
            for t in tags:
                if t not in dic_tags:
                    dic_tags[t] = 0
                dic_tags[t] = dic_tags[t] + 1

        tags = []
        for tag in dic_tags:
            if len(tag.strip()) == 0:
                continue
            if dic_tags[tag] > 1:
                tags.append(tag)
        n_content = wiki.pages.get(text).replace('_', '').replace('‌', '')
        all_tags = self.get_all_tags()
        for tag in all_tags:
            if tag in tags:
                continue
            if len(tag.strip()) == 0:
                continue
            # self.send_message('"' + tag + '"', chat_id)
            n_tag = tag.replace('_', '')
            if n_tag in n_content:
                tags.append(tag)

        real_tags = self.get_tags(text)
        x = []
        bef = []
        for i in range(len(tags)):
            if i % 2 == 0:
                x.append(bef)
                bef = []
            if tags[i] in real_tags:
                bef.append({"text": tags[i] + emojies["positive"],
                            "callback_data": 'deletetag_' + str(name_to_id(tags[i]))})
            else:
                bef.append({"text": tags[i] + emojies["negative"],
                            "callback_data": 'addtag_' + str(name_to_id(tags[i]))})
        x.append(bef)
        x.append([{"text": 'پایان' + emojies["finish"], "callback_data": 'finish'}])

        user.cache = text
        user.cache1 = json.dumps(tags)
        user.save()
        self.edit_message(message['message_id'], chat_id,
                          'خیلی ممنون. '
                          'برچسب‌گذاری بخش بسایر مهمی از ویکی‌ست و باعث می‌شود دسترسی به مستندات و صفحات آسان‌تر شود. '
                          'کارشناسان ویکی‌یار لیست برچسب‌های زیر را برای این صفحه پیشنهاد داده‌اند. '
                          'لطفا در صورت تطابق تعدادی از برچسب‌های زیر را استفاده کنید'
                          ' و در صورتی که برچسب دیگری نیز صلاح می‌دانید به صورت دستی وارد بفرماید.',
                          reply_markup={"inline_keyboard": x})

    # telegram functions
    @staticmethod
    def edit_message(message_id, chat_id, text, reply_markup=None):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup is not None:
            data["reply_markup"] = json.dumps(reply_markup)
        r = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/editMessageText", data=data
        )

    @staticmethod
    def delete_message(message_id, chat_id):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
        }
        r = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/deleteMessage", data=data
        )

    @staticmethod
    def send_message(message, chat_id, reply_markup=None):
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }
        if reply_markup is not None:
            data["reply_markup"] = json.dumps(reply_markup)
        r = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendMessage", data=data
        )
        j = json.loads(r.text)
        return j["result"]

    @staticmethod
    def send_document(fname, chat_id):
        file = open(fname, 'rb')
        # file = fname
        data = {
            "chat_id": chat_id
        }
        files = {
            "document": file
        }
        r = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendDocument", data=data, files=files
        )


#
#
#
#
#
#
#
#
#
#
# def migrate(update, context):
#     try:
#         if update.message.from_user.username != admin_username:
#             return
#         init_db()
#         update.message.reply_text('چشم استاد.')
#     except NameError as ne:
#         print(ne)
#     except:
#         print(sys.exc_info()[0])
#
#
# def send_messages(update, context):
#     try:
#         if update.message.from_user.username != admin_username:
#             return
#         f = open('msgs.txt', 'r', encoding='UTF-8')
#         for line in f.read().strip().split('\n'):
#             l = line.split(',')
#             if l[0] == 'all':
#                 for user in db_session.query(User).all():
#                     context.bot.send_message(user.tlg_id, l[1].replace('<<name>>', user.persian_name))
#             else:
#                 # print(db_session.query(User).filter(User.username==l[0][1:]).all())
#                 user = db_session.query(User).filter(User.username == l[0][1:]).all()[0]
#                 context.bot.send_message(user.tlg_id, l[1].replace('<<name>>', user.persian_name))
#     except NameError as ne:
#         print(ne)
#     except telegram.error.BadRequest as e:
#         print(e)
#     except IndexError as e:
#         print(e)
#     except telegram.error.Unauthorized as e:
#         print(e)
#     except:
#         print(sys.exc_info()[0])
