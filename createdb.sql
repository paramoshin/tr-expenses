create table expense (
    id integer PRIMARY KEY,
    amount float,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

