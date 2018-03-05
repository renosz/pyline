import os
from flask import Flask, request, abort

from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage, SourceGroup, SourceRoom
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
	
	if text == '/help':
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage("Bison bisa diusir sekarang. \n"
							"Sama ada command 'Stalk'"))
	
	elif text == 'Stalk':
		try:
			profile = line_bot_api.get_profile(event.source.user_id)
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage("Display name: " + profile.display_name + "\n" +
								"Profile picture: " + profile.picture_url + "\n" +
								"User_ID: " + profile.user_id + "\n" +
								"Status Message: " + profile.status_message))
		except LineBotApiError:
			pass
			
	elif text == 'Pergi lu Son':
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)