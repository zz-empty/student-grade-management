cmake_minimum_required(VERSION 3.10)
project(student_system C)

# 设置C标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 查找cJSON库
find_library(CJSON_LIBRARY NAMES cjson)
find_path(CJSON_INCLUDE_DIR NAMES cjson/cJSON.h)

if(NOT CJSON_LIBRARY OR NOT CJSON_INCLUDE_DIR)
    message(FATAL_ERROR "cJSON library not found. Install with 'brew install cjson'")
endif()

# 添加可执行文件
add_executable(student_system
    src/student.c
    src/hash_table.c
    src/json_io.c
    src/main.c
)

# 包含目录
target_include_directories(student_system PRIVATE
    ${CJSON_INCLUDE_DIR}
    src/
)

# 链接库
target_link_libraries(student_system ${CJSON_LIBRARY})

# 复制测试数据到构建目录
configure_file(data/students.json ${CMAKE_BINARY_DIR}/students.json COPYONLY)
