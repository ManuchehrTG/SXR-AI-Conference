import json
from datetime import datetime
from typing import List

from infrastructure.database import db

class AnalyticsRepository:
	@staticmethod
	async def get_conversion_analytics():
		records = await db.fetch(
			"""
			SELECT 
				'STUDIO' as offer_type,
				COUNT(DISTINCT CASE WHEN e.type = 'click_studio' THEN e.user_id END) as clicks,
				COUNT(DISTINCT CASE WHEN e.type = 'studio_coupon_issued' THEN e.user_id END) as conversions
			FROM events e
			WHERE e.type IN ('click_studio', 'studio_coupon_issued')

			UNION ALL

			SELECT 
				'COURSE' as offer_type,
				COUNT(DISTINCT CASE WHEN e.type = 'click_course' THEN e.user_id END) as clicks,
				COUNT(DISTINCT CASE WHEN e.type = 'course_promocodes_issued' THEN e.user_id END) as conversions
			FROM events e
			WHERE e.type IN ('click_course', 'course_promocodes_issued')

			UNION ALL

			SELECT 
				'CLUB' as offer_type,
				COUNT(DISTINCT CASE WHEN e.type = 'click_club' THEN e.user_id END) as clicks,
				COUNT(DISTINCT CASE WHEN e.type = 'club_paid' THEN e.user_id END) as conversions
			FROM events e
			WHERE e.type IN ('click_club', 'club_paid');
			"""
		)
		return records
