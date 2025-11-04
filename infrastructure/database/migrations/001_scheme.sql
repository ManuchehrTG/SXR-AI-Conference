-- DELETE TABLE
-- DROP TABLE IF EXISTS subscription_transactions, subscriptions, transactions, events, users;

-- CREATE TABLE
CREATE TABLE IF NOT EXISTS users (
	id					BIGINT						PRIMARY KEY,
	first_name			TEXT						NOT NULL,
	username			TEXT,
	language_code		TEXT						NOT NULL,
	email				TEXT,
	agreed_privacy		BOOLEAN						DEFAULT FALSE,
	studio_coupon_used	BOOLEAN						DEFAULT FALSE,
	is_admin			BOOLEAN						DEFAULT FALSE,
	source				TEXT,
	created_at			TIMESTAMP WITH TIME ZONE	DEFAULT now(),
	updated_at			TIMESTAMP WITH TIME ZONE	DEFAULT now()
);

CREATE TABLE IF NOT EXISTS events (
	id					SERIAL						PRIMARY KEY,
	user_id				BIGINT						NOT NULL REFERENCES users(id),
	type				TEXT						NOT NULL,
	meta				JSONB						DEFAULT '{}'::jsonb,
	ts					TIMESTAMP WITH TIME ZONE	DEFAULT now(),
	UNIQUE (user_id, type)
);

CREATE TABLE IF NOT EXISTS transactions (
	id					UUID						PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id				BIGINT						NOT NULL REFERENCES users(id),
	offer				TEXT						NOT NULL,
	type				TEXT						NOT NULL CHECK (type IN ('subscription', 'product')),
	amount				NUMERIC(12, 2)				NOT NULL,
	quantity			NUMERIC(12, 2)				NOT NULL,
	provider_tx_id		TEXT						NOT NULL,
	provider_payload	JSONB						NOT NULL,
	status				TEXT						NOT NULL,
	created_at			TIMESTAMP WITH TIME ZONE	DEFAULT now(),
	updated_at			TIMESTAMP WITH TIME ZONE	DEFAULT now()
);

CREATE TABLE IF NOT EXISTS subscriptions (
	id					SERIAL						PRIMARY KEY,
	user_id				BIGINT						NOT NULL REFERENCES users(id),
	offer				TEXT						NOT NULL,
	status				TEXT						CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
	started_at			TIMESTAMP WITH TIME ZONE	NOT NULL,
	expires_at			TIMESTAMP WITH TIME ZONE	NOT NULL,
	updated_at			TIMESTAMP WITH TIME ZONE	NOT NULL
);

CREATE TABLE IF NOT EXISTS subscription_transactions (
	sub_id				INT							REFERENCES subscriptions(id),
	tx_id				UUID						REFERENCES transactions(id),
	type				TEXT						CHECK (type IN ('initial', 'renewal'))
);
