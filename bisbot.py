import errno
import os
import sys
import tempfile
from argparse import ArgumentParser
from urllib.parse import quote
from kbbi import KBBI
import requests
import wikipedia
from flask import Flask, request, abort
from googletrans import Translator
from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, SourceGroup, SourceRoom,
	TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
	ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
	PostbackTemplateAction, DatetimePickerTemplateAction,
	CarouselTemplate, CarouselColumn, PostbackEvent,
	StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
	ImageMessage, VideoMessage, AudioMessage, FileMessage,
	UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

wiki_settings = {}
translator = Translator()
app = Flask(__name__)

line_bot_api = LineBotApi('0MZ23nJcb0Rtcn4jkjdm/RjNS07Dx7zj34q2SE84mlbZbrtoGunYlxb6jDIvcYisd+gyBuzGROVx0JGTPoi3DWCQHbm8YJ5aycbWf4gAL7RGx+/b/J2Kkb75Vh7Qo2NmGwi3MDQzUYPAFmbocQypWAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('4350db3555e5530136cd07b53fa4091a')


@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

	text=event.message.text
	
	if isinstance(event.source, SourceGroup):
		subject = line_bot_api.get_group_member_profile(event.source.group_id,
														event.source.user_id)
		set_id = event.source.group_id
	elif isinstance(event.source, SourceRoom):
		subject = line_bot_api.get_room_member_profile(event.source.room_id,
                                                   event.source.user_id)
		set_id = event.source.room_id
	else:
		subject = line_bot_api.get_profile(event.source.user_id)
		set_id = event.source.user_id
		
	def spilit1(text):
		return text.split('/wolfram ', 1)[-1]
	
	def spilit2(text):
		return text.split('/kbbi ', 1)[-1]
		
	def split3(text):
		return text.split('/echo ', 1)[-1]

	def split4(text):
		return text.split('/wolframs ', 1)[-1]
		
	def split5(text):
		return text.split('/trans ', 1)[-1]
	
	def split6(text):
		return text.split('/wiki ', 1)[-1]
	
	def split7(text):
		return text.split('/wikilang ', 1)[-1]
			
	def wolframs(query):
		wolfram_appid = ('83L4JP-TWUV8VV7J7')

		url = 'https://api.wolframalpha.com/v2/simple?i={}&appid={}'
		return url.format(quote(query), wolfram_appid)
	
	def wolfram(query):
		wolfram_appid = ('83L4JP-KWW62H4Y96')

		url = 'https://api.wolframalpha.com/v2/result?i={}&appid={}'
		return requests.get(url.format(quote(query), wolfram_appid)).text
	
	def trans(word):
		sc = 'id'
		to = 'en'
		
		if word[0:].lower().strip().startswith('sc='):
			sc = word.split(', ', 1)[0]
			sc = sc.split('sc=', 1)[-1]
			word = word.split(', ', 1)[1]
	
		if word[0:].lower().strip().startswith('to='):
			to = word.split(', ', 1)[0]
			to = to.split('to=', 1)[-1]
			word = word.split(', ', 1)[1]
			
		if word[0:].lower().strip().startswith('sc='):
			sc = word.split(', ', 1)[0]
			sc = sc.split('sc=', 1)[-1]
			word = word.split(', ', 1)[1]
			
		return translator.translate(word, src=sc, dest=to).text
		
	def wiki_get(keyword, set_id, trim=True):
    
		try:
			wikipedia.set_lang(wiki_settings[set_id])
		except KeyError:
			wikipedia.set_lang('en')

		try:
			result = wikipedia.summary(keyword)

		except wikipedia.exceptions.DisambiguationError:
			articles = wikipedia.search(keyword)
			result = "{} disambiguation:".format(keyword)
			for item in articles:
				result += "\n{}".format(item)
		except wikipedia.exceptions.PageError:
			result = "{} not found!".format(keyword)

		else:
			if trim:
				result = result[:2000]
				if not result.endswith('.'):
					result = result[:result.rfind('.')+1]
		return result
		
	def wiki_lang(lang, set_id):
    
		langs_dict = wikipedia.languages()
		if lang in langs_dict.keys():
			wiki_settings[set_id] = lang
			return ("Language has been changed to {} successfully."
					.format(langs_dict[lang]))

		return ("{} not available!\n"
				"See meta.wikimedia.org/wiki/List_of_Wikipedias for "
				"a list of available languages, and use the prefix "
				"in the Wiki column to set the language."
				.format(lang))	
	
	def find_kbbi(keyword, ex=False):

		try:
			entry = KBBI(keyword)
		except KBBI.TidakDitemukan as e:
			result = str(e)
		else:
			result = "Definisi {}:\n".format(keyword)
			if ex:
				result += '\n'.join(entry.arti_contoh)
			else:
				result += str(entry)
		return result
	
	if text == 'key':
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage("/Kickme. \n"
							"Myinfo \n"
							"/wolfram {input} juga bisa"))
	
	elif text == 'myinfo':
		if isinstance(event.source, SourceGroup):
			try:
				profile = line_bot_api.get_group_member_profile(event.source.group_id, event.source.user_id)
				line_bot_api.reply_message(
					event.reply_token,
					TextSendMessage("Display name: " + profile.display_name + "\n" +
									"Profile picture: " + profile.picture_url + "\n" +
									"User_ID: " + profile.user_id))
			except LineBotApiError:
				pass
		
		elif isinstance(event.source, SourceRoom):
			try:
				profile = line_bot_api.get_room_member_profile(event.source.room_id, event.source.user_id)
				line_bot_api.reply_message(
					event.reply_token,
					TextSendMessage("Display name: " + profile.display_name + "\n" +
									"Profile picture: " + profile.picture_url + "\n" +
									"User_ID: " + profile.user_id))
			except LineBotApiError:
				pass
				
		else:
			try:
				profile = line_bot_api.get_profile(event.source.user_id)
				line_bot_api.reply_message(
					event.reply_token,
					TextSendMessage("Display name: " + profile.display_name + "\n" +
									"Profile picture: " + profile.picture_url + "\n" +
									"User_ID: " + profile.user_id))
			except LineBotApiError:
				pass
			
	elif (text == 'bot @bye') or (text== '@bye'):
		if isinstance(event.source, SourceGroup):
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage('Creator : https://goo.gl/KL5D5y'))
			line_bot_api.leave_group(event.source.group_id)
		
		elif isinstance(event.source, SourceRoom):
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage('Creator : https://goo.gl/KL5D5y'))
			line_bot_api.leave_room(event.source.room_id)
			
		else:
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage('Ga mau keluar>_<'))

	elif text=='/wolfram':
		line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage('command /wolfram {input}'))
	
	elif text=='/kickme':
		groupId = event.source.group_id
		contactIds = ua1b0404572c8c160e587b1b09db53831
		line_bot_api.kickoutFromGroup(0, groupId, contactIds)
				
	elif text[0:].lower().strip().startswith('/wolfram '):
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(wolfram(spilit1(text))))
			
	elif text[0:].lower().strip().startswith('/kbbi '):
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(find_kbbi(spilit2(text))))
			
	elif text[0:].lower().strip().startswith('/wolframs '):
		line_bot_api.reply_message(
			event.reply_token,
			ImageSendMessage(original_content_url= wolframs(split4(text)),
								preview_image_url= wolframs(split4(text))))
								
	elif text[0:].lower().strip().startswith('/echo ') :
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(split3(text)))
			
	elif text[0:].lower().strip().startswith('/trans ') :
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(trans(split5(text))))
	
	elif text[0:].lower().strip().startswith('/wiki ') :
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(wiki_get(split6(text), set_id=set_id)))
			
	elif text[0:].lower().strip().startswith('/wikilang ') :
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(wiki_lang(split7(text), set_id=set_id)))
	
			
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
	line_bot_api.reply_message(
		event.reply_token,
		StickerSendMessage(
			package_id=event.message.package_id,
			sticker_id=event.message.sticker_id)
	)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
	line_bot_api.reply_message(
		event.reply_token,
		LocationSendMessage(
			title=event.message.title, address=event.message.address,
			latitude=event.message.latitude, longitude=event.message.longitude
		)
	)

@handler.add(JoinEvent)
def handle_join(event):
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text='Barista is here... ' + event.source.type + ' apa ini?'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
