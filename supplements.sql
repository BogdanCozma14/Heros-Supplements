CREATE TABLE products(
	id SERIAL PRIMARY KEY,
	url_image TEXT,
	description TEXT,
	price NUMERIC(10,2),
	category TEXT
);