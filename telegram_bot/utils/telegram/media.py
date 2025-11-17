from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from typing import Dict, List

class MediaProcessing:
	@staticmethod
	def pack(media_files: List[Message | Dict]) -> List[InputMediaPhoto | InputMediaVideo]:
		media = [
			InputMediaPhoto(media=message.photo[-1].file_id)
			if message.photo else
			InputMediaVideo(media=message.video.file_id)
			for message in media_files
		] if isinstance(media_files[0], Message) else [
			InputMediaPhoto(media=media_file["media"])
			if media_file["type"] == "photo" else
			InputMediaVideo(media=media_file["media"])
			for media_file in media_files
		]

		if media and media_files:
			media[0].caption = (
				media_files[0].caption
				if isinstance(media_files[0], Message) else
				media_files[0].get("caption")
			)

		return media

	@staticmethod
	def parse_media_messages(albom: List[Message]):
		media = [
			{"type": "photo", "media": message.photo[-1].file_id}
			if message.photo else
			{"type": "video", "media": message.video.file_id}
			for message in albom
		]

		if media and albom[0].caption:
			media[0]["caption"] = albom[0].html_text
			media[0]["parse_mode"] = "HTML"
			# media[0]["html_text"] = albom[0].html_text

		return media
