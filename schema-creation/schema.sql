DROP TABLE IF EXISTS user_topic;
DROP TABLE IF EXISTS mention;
DROP TABLE IF EXISTS topic;
DROP TABLE IF EXISTS users;





CREATE TABLE users (
    user_id INT PRIMARY KEY,
    email TEXT NOT NULL,
    phone_number TEXT NOT NULL
);

CREATE TABLE topic (
    topic_id INT PRIMARY KEY,
    topic_name TEXT NOT NULL
);

CREATE TABLE user_topic (
    user_topic_id BIGINT PRIMARY KEY,
    user_id INT NOT NULL,
    topic_id INT NOT NULL,
    active BOOLEAN NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (topic_id) REFERENCES topic (topic_id)
);

CREATE TABLE mention(
    mention_id BIGINT PRIMARY KEY,
    topic_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    sentiment_label TEXT NOT NULL,
    sentiment_score FLOAT(53) NOT NULL,
    FOREIGN KEY(topic_id) REFERENCES topic (topic_id)
);

