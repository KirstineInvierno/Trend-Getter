DROP SCHEMA IF EXISTS bluesky CASCADE;


CREATE SCHEMA bluesky;


CREATE TABLE bluesky.users (
    user_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email TEXT UNIQUE CHECK(email LIKE '%_@_%._%'),
    phone_number TEXT UNIQUE NOT NULL
);

CREATE TABLE bluesky.topic (
    topic_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    topic_name TEXT UNIQUE NOT NULL
);

CREATE TABLE bluesky.user_topic (
    user_topic_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT NOT NULL,
    topic_id INT NOT NULL,
    active BOOLEAN NOT NULL,
    threshold INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES bluesky.users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES bluesky.topic (topic_id) ON DELETE CASCADE
);

CREATE TABLE bluesky.mention(
    mention_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    topic_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    sentiment_label TEXT NOT NULL,
    sentiment_score FLOAT(53) NOT NULL,
    FOREIGN KEY(topic_id) REFERENCES bluesky.topic (topic_id) ON DELETE CASCADE
);

