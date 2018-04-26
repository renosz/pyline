import errno
import os
import sys
import tempfile
from argparse import ArgumentParser
from urllib.parse import quote
from kbbi import KBBI
import requests
from flask import Flask, request, abort
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

app = Flask(__name__)

line_bot_api = LineBotApi('CzSF4tZw1pR4X9i8Y6s580+0p7ebCpqq9MpoA98z8zsAl1ObHL+/Bmsk0t6BRk2+W9bxrNQMsUDsiEFcwr3nF7lVx644o8HwAXfr7mMfVhyXPC88CoNZKZxETv+WLa0L/gZoHA3YMc9KFINKeeoP+gdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f69e514026a91f8ba1e5e3c7934eca35')


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
	
	def spilit1(text):
		return text.split('/wolfram ', 1)[-1]
	
	def spilit2(text):
		return text.split('/kbbi ', 1)[-1]
		
	def split3(text):
		return text.split('/echo ', 1)[-1]

	def split4(text):
		return text.split('/wolframs ', 1)[-1]
		
	def wolframs(query):
		wolfram_appid = ('83L4JP-TWUV8VV7J7')

		url = 'https://api.wolframalpha.com/v2/simple?i={}&appid={}'
		return url.format(quote(query), wolfram_appid)
	
	def wolfram(query):
		wolfram_appid = ('83L4JP-KWW62H4Y96')

		url = 'https://api.wolframalpha.com/v2/result?i={}&appid={}'
		return requests.get(url.format(quote(query), wolfram_appid)).text

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
	
	if text == '/help':
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage("Bison bisa diusir sekarang. \n"
							"Sama ada command 'Stalk' \n"
							"/wolfram {input} juga bisa"))
	
	elif text == 'Stalk':
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
			
	elif (text == 'Pergi lu Son') or (text== 'Enyah lu Son'):
		if isinstance(event.source, SourceGroup):
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage('Bye.'))
			line_bot_api.leave_group(event.source.group_id)
		
		elif isinstance(event.source, SourceRoom):
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage('Bye.'))
			line_bot_api.leave_room(event.source.room_id)
			
		else:
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage('Gabisa dodol.'))

	elif text=='/wolfram':
		line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage('command /wolfram {input}'))
				
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