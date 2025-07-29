DROP TABLE IF EXISTS user_topic;
DROP TABLE IF EXISTS mention;
DROP TABLE IF EXISTS topic;
DROP TABLE IF EXISTS users;





CREATE TABLE users (
    user_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email TEXT UNIQUE NOT NULL CHECK(email LIKE '%_@_%._%'),
    phone_number TEXT UNIQUE NOT NULL
);

CREATE TABLE topic (
    topic_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    topic_name TEXT UNIQUE NOT NULL
);

CREATE TABLE user_topic (
    user_topic_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT NOT NULL,
    topic_id INT NOT NULL,
    active BOOLEAN NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (topic_id) REFERENCES topic (topic_id)
);

CREATE TABLE mention(
    mention_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    topic_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    sentiment_label TEXT NOT NULL,
    sentiment_score FLOAT(53) NOT NULL,
    FOREIGN KEY(topic_id) REFERENCES topic (topic_id)
);

