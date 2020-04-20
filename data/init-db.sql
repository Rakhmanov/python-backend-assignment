BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "sessions" (
	"id"	VARCHAR NOT NULL,
	"user_id"	INTEGER,
	"client_ip"	VARCHAR,
	"timestamp"	DATETIME DEFAULT (datetime('now')),
	"expiry"	DATETIME DEFAULT (datetime('now','30 minutes')),
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "access_logs" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER,
	"client_ip"	VARCHAR,
	"resource"	VARCHAR,
	"method"	VARCHAR,
	"body"	BLOB,
	"timestamp"	DATETIME DEFAULT (datetime('now')),
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "animals" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR,
	"species"	VARCHAR,
	"author_id"	INTEGER,
	PRIMARY KEY("id"),
	FOREIGN KEY("author_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR,
	"last_name"	VARCHAR,
	"email"	VARCHAR,
	"password"	VARCHAR,
	PRIMARY KEY("id")
);
CREATE UNIQUE INDEX IF NOT EXISTS "ix_users_email" ON "users" (
	"email"
);
COMMIT;

INSERT INTO animals VALUES 
    (1, 'Alice', 'Kangaroo', NULL),
    (2, 'Eva', 'Penguin', NULL),
    (3, 'Oliver', 'Giraffe', NULL),
    (4, 'Liam', 'Panda', NULL),
    (5, 'Sophia', 'Hippo', NULL),
    (6, 'Mia', 'Gorilla', NULL),
    (7, 'Lucas', 'Penguin', NULL),
    (8, 'Luna', 'Penguin', NULL),
    (9, 'Grace', 'Kangaroo', NULL),
    (10, 'Oliver', 'Gorilla', NULL),
    (11, 'Mars', 'Cat', 2),
    (12, 'Ryzhii', 'Cat', 2),
    (13, 'Peludo', 'Cat', 1),
    (14, 'Flojo', 'Cat', 1),
    (15, 'Gordo', 'Cat', 1)
;

INSERT INTO users VALUES 
    (1, 'Denis', 'Shatilov', 'shatilov18@gmail.com', 'afeb223bc69b7a84eab7399f4fa18ca4d3dd4db309f62b95aef076b5234e6f525f81040ec3e9faefebc90b8cc62ad4b0f61c10980c654f7244cf71eba7ab5aa170f6a1d7e72a07f663b4a2c636d45bf16d1b79c6878131ab676d748f5ddef1b2')
;
