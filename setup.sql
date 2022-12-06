CREATE TABLE "users" (
    userid VARCHAR(32) NOT NULL,
    username VARCHAR(255) NOT NULL,
    useremail VARCHAR(255) NOT NULL,
    salt VARCHAR NOT NULL,
    createat BIGINT NOT NULL,
    lastmodifiedat BIGINT NOT NULL,
    status INT NOT NULL DEFAULT 0
);

CREATE TABLE "passwords" (
    pwdid VARCHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    description VARCHAR NULL,
    sensitiveinfo VARCHAR NULL,
    userid VARCHAR(32) NOT NULL,
    createat BIGINT NOT NULL,
    lastmodifiedat BIGINT NOT NULL,

    FOREIGN KEY (userid) REFERENCES "users"(userid)
);