CREATE TABLE "Message" (
  "topic_id" uuid NOT NULL,
  "message_id" uuid NOT NULL,
  "text" varchar(4096) NOT NULL,
  "created_at" timestamp NOT NULL,
  "updatet_at" timestamp NOT NULL,
  "author_id" int4 NOT NULL,
  CONSTRAINT "_copy_1" PRIMARY KEY ("topic_id", "message_id")
);

CREATE TABLE "Topic" (
  "topic_id" int4 NOT NULL,
  "topic_name" varchar(255),
  PRIMARY KEY ("topic_id")
);

CREATE TABLE "Topic_user" (
  "topic_id" int4 NOT NULL,
  "user_id" int4 NOT NULL,
  "permitions" varchar(255),
  CONSTRAINT "_copy_5" PRIMARY KEY ("topic_id", "user_id")
);

CREATE TABLE "User" (
  "user_id" int4 NOT NULL,
  "username" varchar(255) NOT NULL,
  "email" varchar(255),
  "name" varchar(255),
  "surname" varchar(255),
  "hashed_password" varchar(255),
  "is_active" varchar(255),
  "hashed_password" varchar(255),
  CONSTRAINT "_copy_2" PRIMARY KEY ("user_id")
);

