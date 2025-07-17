#!/usr/bin/env bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

show_help() {
    cat <<EOF
Usage:  ./setup-mysql-env.sh
                Interactively configure database parameters to .env file.
        ./setup-mysql-env.sh [options]
                Call the function corresponding to option.

Options:
    -h, --help Display this help message
    -t, --test Use parameters in .env to test the database connection
EOF
}

print_message() {
    local type=$1
    local message=$2
    case $type in
    "info")
        echo -e "${BLUE}$message${NC}"
        ;;
    "success")
        echo -e "${GREEN}$message${NC}"
        ;;
    "error")
        echo -e "${RED}$message${NC}"
        ;;
    *)
        echo -e "${BLUE}$message${NC}"
        ;;
    esac
}

get_user_input() {
    local prompt="$1"
    local default="$2"
    local user_input

    if [ -n "$default" ]; then
        read -p "$(echo -e $BLUE"$prompt [Default: $default]: "$NC)" user_input
        echo "${user_input:-$default}"
    else
        read -p "$(echo -e $BLUE"$prompt: "$NC)" user_input
        echo "$user_input"
    fi
}

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_message "success" "Copied .env.example into .env successfully"
    else
        print_message "error" "ERROR: .env.example not found"
        exit 1
    fi
fi

update_env() {
    local key=$1
    local value=$2
    local file=".env"

    if grep -q "^${key}=" "$file"; then
        if [ "$(uname)" == "Darwin" ]; then
            sed -i '' "s|^${key}=.*|${key}=${value}|" "$file"
        else
            sed -i "s|^${key}=.*|${key}=${value}|" "$file"
        fi
        if [ $? -ne 0 ]; then
            if [ "$(uname)" == "Darwin" ]; then
                sed -i '' "s|^${key}=.*|#${key}=|" "$file" 2&1 >/dev/null
            else
                sed -i "s|^${key}=.*|#${key}=|" "$file" 2&1 >/dev/null
            fi
            echo "${key}=${value}" >>"$file"
        fi
    else
        echo "${key}=${value}" >>"$file"
    fi
}

CURRENT_HOST=$(hostname -i)

print_message "info" "Please fill in the database parameters:"

USE_OB_DOCKER=$(get_user_input "Use the OceanBase container started by Docker Compose as the metadata database and vector storage?  Y or N:" "Y")
COMPOSE_PROFILES="oceanbase"

if [ "$USE_OB_DOCKER" == "Y" ]; then
    print_message "info" "Trying to use docker compose to start OceanBase as metadata and vector database, please set following parameters for it."
    DB_HOST=$(get_user_input "Current Host" "$CURRENT_HOST")
    DB_PORT=$(get_user_input "OceanBase Port" "2881")
    DB_USERNAME="root@test"
    DB_PASSWORD=$(get_user_input "OceanBase Password for user 'root@test'" "difyai123456")
    DB_DATABASE="test"
    DB_PLUGIN_DATABASE=$(get_user_input "Plugin Database Name (Will be created by the application, must not be 'test')" "dify_plugin")

    USE_AS_VECTOR_STORE="Y"
    OCEANBASE_VECTOR_DATABASE="test"
else
    print_message "info" "Trying to use existing MySQL/OceanBase, please fill in the following parameters about it."
    DB_HOST=$(get_user_input "Database Host" "${CURRENT_HOST}")
    DB_PORT=$(get_user_input "Database Port" "2881")
    DB_USERNAME=$(get_user_input "Database Username" "root@test")
    DB_PASSWORD=$(get_user_input "Database Password" "difyai123456")
    DB_DATABASE=$(get_user_input "Database Name (You need create it first)" "test")
    DB_PLUGIN_DATABASE=$(get_user_input "Plugin Database Name (Will be created if not exists, must not be the same with 'Database Name' option)" "dify_plugin")

    USE_AS_VECTOR_STORE=$(get_user_input "It's OceanBase and want to use it also as the vector store?  Y or N:" "N")
    if [ "$USE_AS_VECTOR_STORE" == "Y" ]; then
        OCEANBASE_VECTOR_DATABASE=$(get_user_input "Vector Database Name (You need create it first)" "test")
        COMPOSE_PROFILES=""
    fi
fi

if [ "$USE_AS_VECTOR_STORE" == "Y" ]; then
    update_env "OCEANBASE_VECTOR_HOST" "$DB_HOST"
    update_env "OCEANBASE_VECTOR_PORT" "$DB_PORT"
    update_env "OCEANBASE_VECTOR_USER" "$DB_USERNAME"
    update_env "OCEANBASE_VECTOR_PASSWORD" "$DB_PASSWORD"
    update_env "OCEANBASE_VECTOR_DATABASE" "$OCEANBASE_VECTOR_DATABASE"
fi

update_env "SQLALCHEMY_DATABASE_URI_SCHEME" "mysql+pymysql"
update_env "DB_TYPE" "mysql"
update_env "DB_HOST" "$DB_HOST"
update_env "DB_PORT" "$DB_PORT"
update_env "DB_USERNAME" "$DB_USERNAME"
update_env "DB_PASSWORD" "$DB_PASSWORD"
update_env "DB_DATABASE" "$DB_DATABASE"

update_env "DB_PLUGIN_DATABASE" "$DB_PLUGIN_DATABASE"

update_env "COMPOSE_PROFILES" "$COMPOSE_PROFILES"
update_env "VECTOR_STORE" "oceanbase"
update_env "PIP_MIRROR_URL" "https://pypi.tuna.tsinghua.edu.cn/simple"

# Redis configuration
USE_REDIS=$(get_user_input "Use Redis for caching?  Y or N:" "N")

if [ "$USE_REDIS" == "Y" ]; then
    print_message "info" "Configuring Redis cache..."
    
    # Check if docker-compose-redis.yaml exists
    if [ -f "docker-compose-redis.yaml" ]; then
        print_message "info" "Found docker-compose-redis.yaml, copying to docker-compose.yaml"
        cp docker-compose-redis.yaml docker-compose.yaml
        
        # Set environment to use Redis
        update_env "CACHE_SCHEME" "redis"
        update_env "CELERY_BROKER_URL" "redis://:difyai123456@redis:6379/1"
        
        print_message "success" "Redis cache configuration completed."
        print_message "info" "Use 'docker-compose up -d' to start services with Redis."
    else
        print_message "error" "ERROR: docker-compose-redis.yaml not found!"
        print_message "info" "Please create docker-compose-redis.yaml with Redis service configuration."
        exit 1
    fi
else
    print_message "info" "Using MySQL cache as default."
    # Copy MySQL configuration to docker-compose.yaml
    if [ -f "docker-compose-mysql.yaml" ]; then
        print_message "info" "Found docker-compose-mysql.yaml, copying to docker-compose.yaml"
        cp docker-compose-mysql.yaml docker-compose.yaml
    fi
    print_message "info" "Using MySQL cache as default."
    update_env "CACHE_SCHEME" "mysql"
    update_env "OCEANBASE_CLUSTER_NAME" "difyai-redis"
    
    # Update CELERY_BROKER_URL for MySQL cache with proper URL encoding
    # URL encode the username to handle special characters like @
    ENCODED_USERNAME=$(echo "$DB_USERNAME" | sed 's/@/%40/g')
    CELERY_BROKER_URL="sqla+mysql+pymysql://${ENCODED_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_DATABASE}"
    update_env "CELERY_BROKER_URL" "$CELERY_BROKER_URL"
    print_message "success" "CELERY_BROKER_URL updated for MySQL cache."
fi

print_message "success" "\nDatabase parameters are written into .env successfully."

print_message "success" "\nConnect to metadata database:"
print_message "success" "\n    mysql -h$DB_HOST -P$DB_PORT -u$DB_USERNAME -p$DB_PASSWORD -D$DB_DATABASE"
