create table profile (
	id int PRIMARY KEY NOT NULL,
	name varchar(10),
	salary int,
	room smallint,
	keywords varchar(50),
	telnum int,
	picture varchar(200)
);

insert into profile(id, name, salary, room, keywords, telnum, picture)
values (1, 'Abhishek', 100000, 550, 'Abhishek is almost done and very smart', 20202020, 'https://cdn3.iconfinder.com/data/icons/social-messaging-productivity-6/128/profile-male-circle2-512.png');

insert into profile(id, name, salary, room, keywords, picture)
values (2, 'Jees', 99099, 420, 'Jees is too', 'https://cdn3.iconfinder.com/data/icons/social-messaging-productivity-6/128/profile-male-circle2-512.png');

insert into profile(id, name, salary, keywords, telnum, picture)
values (3, 'Jason', 99901, 'Is smart and hard working', 1000011, 'https://cdn3.iconfinder.com/data/icons/social-messaging-productivity-6/128/profile-male-circle2-512.png');

insert into profile(id, name, salary, room, keywords, telnum)
values (4, 'Dave', 1, 525, 'Does not seem too nice', 0);