CREATE TABLE if not exists months (
       id integer primary key,
       factor TEXT not null,
       month integer not null,
       index FLOAT not null
);

CREATE TABLE if not exists weeks (
       id integer primary key,
       factor TEXT not null,
       week integer not null,
       index FLOAT not null
);
