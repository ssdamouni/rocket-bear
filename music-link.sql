DROP DATABASE IF EXISTS  cascade_link;
CREATE DATABASE cascade_link;

\c cascade_link
DROP TABLE IF EXISTS instruments;
CREATE TABLE instruments
(
  id SERIAL PRIMARY KEY,
  instrument TEXT NOT NULL
);

INSERT INTO instruments
  (instrument)
VALUES
  ('piano'),
  ('organ'),
  ('harpsichord'),
  ('violin'),
  ('viola'),
  ('cello'),
  ('double bass'),
  ('guitar');

DROP TABLE IF EXISTS voice_types;
CREATE TABLE voice_types(
    id SERIAL PRIMARY KEY,
    voice_type TEXT NOT NULL
);

INSERT INTO voice_types
    (voice_type)
VALUES
    ('coloratura'),
    ('soprano'),
    ('mezzo soprano'),
    ('alto'),
    ('contralto'),
    ('tenor'),
    ('baritone'),
    ('bass');

DROP TABLE IF EXISTS regions;
CREATE TABLE regions(
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    county TEXT NOT NULL,
    state TEXT NOT NULL
);

INSERT INTO regions
    (city, county, state)
VALUES
    ('Seattle', 'King', 'Washington'),
    ('Tacoma', 'Pierce', 'Washington'),
    ('Bremerton', 'Kitsap', 'Washington'),
    ('Olympia', 'Thurston', 'Washington');

DROP TABLE IF EXISTS music_genres;
CREATE TABLE music_genres(
    id SERIAL PRIMARY KEY,
    genre TEXT NOT NULL
);

INSERT INTO music_genres
    (genre)
VALUES
    ('Jazz'),
    ('Classical'),
    ('Country'),
    ('20th and 21st Century Music'),
    ('Historically informed'),
    ('Pop'),
    ('R&B'),
    ('Improvised Music'),
    ('Rock'),
    ('Musical Theatre');

DROP TABLE IF EXISTS user_categories;
CREATE TABLE user_categories(
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL
);

INSERT INTO user_categories
    (category)
VALUES
    ('Teacher'),
    ('Performer'),
    ('Collaborative Pianist'),
    ('Business');

DROP TABLE IF EXISTS education;
CREATE TABLE education(
    id SERIAL PRIMARY KEY,
    degree TEXT NOT NULL
);

INSERT INTO education
    (degree)
VALUES
    ('Bachelors'),
    ('Masters'),
    ('Doctorate'),
    ('Private Studies'),
    ('Self-taught');

DROP TABLE IF EXISTS users;
CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT,
    email TEXT NOT NULL,
    rates TEXT DEFAULT 'Negotiable',
    education_id INTEGER REFERENCES education (id),
    region_id INTEGER REFERENCES regions (id),
    instrument_id INTEGER REFERENCES instruments (id),
    genre_id INTEGER REFERENCES music_genres (id)
)
-- DROP TABLE IF EXISTS user_pieces;
-- CREATE TABLE user_pieces(
--     id SERIAL PRIMARY KEY,
--     title TEXT NOT NULL,
--     composer TEXT NOT NULL,
--     lyricist TEXT DEFAULT 'n/a',
--     user_id INTEGER REFERENCES users (id) ON DELETE CASCADE
-- )
-- INSERT INTO user_pieces(
--     'Fur Elise',
--     'Ludwig van Beethoven'
-- );