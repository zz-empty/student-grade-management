# macOS配置
CC = gcc
CFLAGS = -Wall -g -Iinclude
LDFLAGS = -lreadline -ljansson

# 如果是Linux，可能需要添加 -ljson-c
# UNAME_S := $(shell uname -s)
# ifeq ($(UNAME_S),Linux)
#     LDFLAGS += -ljson-c
# endif

SRC = src/main.c src/menu.c src/utils.c
OBJ = $(SRC:.c=.o)
TARGET = student_frontend

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)

run: all
	./$(TARGET)

.PHONY: all clean run
