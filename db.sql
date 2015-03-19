drop schema if exists alarmdb;

create schema alarmdb;
use alarmdb;

create table alarms(
	id int primary key auto_increment not null,
	uid integer not null,
    date datetime,
    sender integer,
    msg nvarchar(50),
    exp bool);
    
create table friends(
	id1 integer not null,
    id2 integer not null,
    permission bool,
    request int
);

create table users(
	uid integer primary key auto_increment not null,
    email nvarchar(100),
    username nvarchar(20) unique,
	password nvarchar(255),
    app bool,
    salt nvarchar(255),
    session_token nvarchar(255)
);

create view detailed_friends as
	select f.*, u.username, u.email
    from friends f
	inner join users u on f.id2 = u.uid