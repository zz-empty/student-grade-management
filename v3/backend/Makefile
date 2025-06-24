CC = gcc
CFLAGS = -Wall -g -Iinclude
LDFLAGS = -lmysqlclient -ljansson -lpthread

SRC = src/main.c src/db.c src/auth.c src/student.c src/request_handler.c
OBJ = $(SRC:.c=.o)
TARGET = backend_server

# 使用环境变量配置
ENV_CONFIG = -DUSE_ENV_CONFIG

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

env: CFLAGS += $(ENV_CONFIG)
env: $(TARGET)

clean:
	rm -f $(OBJ) $(TARGET)

.PHONY: all env clean
