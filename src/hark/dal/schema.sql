CREATE TABLE machine (
	machine_id char(36) PRIMARY KEY,
	name       varchar(255),
	driver     varchar(255),
	guest      varchar(255),
	memory_mb  INTEGER,

	CONSTRAINT unique_name UNIQUE (name)
);

CREATE TABLE port_mapping (
	host_port  INTEGER PRIMARY KEY,
	guest_port INTEGER,
	machine_id char(36),
	name       varchar(255)
);

CREATE TABLE network_interface (
	machine_id char(36),
	kind       varchar(255),
	label      varchar(255),
	addr       varchar(15),

	PRIMARY KEY (machine_id, kind)
);
