#!/bin/sh

set -x

obclient -h127.0.0.1 -P2881 -uroot@test -p${OB_TENANT_PASSWORD} -e "SELECT 1;"
obclient -h127.0.0.1 -P2881 -uroot@sys -p${OB_SYS_PASSWORD} -e "CREATE USER 'proxyro'@'%' IDENTIFIED BY '123456'; GRANT ALL PRIVILEGES ON *.* TO 'proxyro'@'%'; FLUSH PRIVILEGES;"
# Fixed the bug that obproxy always failed to connect to the test tenant for the first time.
obclient -h127.0.0.1 -P2881 -uroot@sys -p${OB_SYS_PASSWORD} -e "ALTER SYSTEM LOAD MODULE DATA module=redis tenant=sys;"
