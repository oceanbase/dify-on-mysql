import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Mapping

from sqlalchemy import func, or_

from models.engine import db
from models.base import Base

logger = logging.getLogger(__name__)

class Cache(Base):
    __tablename__ = "caches"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="caches_pkey"),
        db.Index("caches_cache_key_idx", "cache_key"),
        db.Index("caches_expire_time_idx", "expire_time"),
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    cache_key = db.Column(db.String(255), nullable=False, unique=True)
    cache_value = db.Column(db.LargeBinary, nullable=False)
    expire_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())


class MysqlRedisClient:
    def __init__(self, meta_db=None):
        self.db = meta_db or db
        self._app = None  # Store Flask app reference

        self._cleanup_thread = None
        self._stop_cleanup = False
        self._start_cleanup_thread()

    def set_app(self, app):
        """Set Flask app reference for cleanup thread"""
        self._app = app

    def cleanup_thread_is_alive(self) -> bool:
        """Check if the cleanup thread is alive"""
        return self._cleanup_thread is not None and self._cleanup_thread.is_alive()

    def _start_cleanup_thread(self):
        """Start background thread for cleaning expired cache entries"""
        if not self.cleanup_thread_is_alive():
            self._stop_cleanup = False
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_expired_cache,
                daemon=True,
                name="MysqlRedisClient-Cleanup"
            )
            self._cleanup_thread.start()
            logger.info("Started background cache cleanup thread")

    def _cleanup_expired_cache(self):
        """Background thread function to clean expired cache entries every 5 minutes"""
        time.sleep(60)

        while not self._stop_cleanup and self.db:
            try:
                # Use Flask app context if available
                if self._app:
                    with self._app.app_context():
                        self.cleanup_expired()
                else:
                    # Fallback without app context
                    self.cleanup_expired()
            except Exception as e:
                logger.warning(f"Error during background cache cleanup: {e}")

            time.sleep(300)

        logger.info("Cache cleanup thread stopped")

    def cleanup_expired(self) -> int:
        """Manually clean expired cache entries and return the number of deleted records"""
        if not self.db:
            return 0

        try:
            expired_count = self.db.session.query(Cache).filter(
                Cache.expire_time.isnot(None),
                Cache.expire_time < datetime.now()
            ).delete()
            self.db.session.commit()
            return expired_count
        except Exception as e:
            logger.warning(f"Error during manual cache cleanup: {e}")
            try:
                self.db.session.rollback()
            except Exception as rollback_error:
                logger.warning(f"Error during rollback: {rollback_error}")
            return 0

    def stop_cleanup(self, sync: bool = True):
        """Stop the background cleanup thread"""
        self._stop_cleanup = True
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            if sync:
                self._cleanup_thread.join(timeout=5)
            logger.info("Cache cleanup thread stopped")

    def pipeline(self) -> 'MysqlRedisClient':
        return self

    def get(self, name: str) -> Optional[bytes]:
        if not self.db:
            return None
        try:
            cache_item = self.db.session.query(Cache).filter(
                Cache.cache_key == name,
                or_(
                    Cache.expire_time.is_(None),
                    Cache.expire_time > datetime.now()
                )
            ).first()

            return cache_item.cache_value if cache_item else None
        except Exception as e:
            logger.warning("MySQLRedisClient.get " + str(name) + " got exception: " + str(e))
            return None

    def set(self, name: str, value, ex: None | int | timedelta = None) -> None:
        if not self.db:
            return

        if not isinstance(value, bytes):
            value = (str(value)).encode('utf-8')

        expire_time = None
        if ex:
            expire = ex if isinstance(ex, timedelta) else timedelta(seconds=ex)
            expire_time = datetime.now() + expire

        try:
            # 使用 INSERT ... ON DUPLICATE KEY UPDATE 避免竞态条件
            sql = """
            INSERT INTO caches (cache_key, cache_value, expire_time) 
            VALUES (:cache_key, :cache_value, :expire_time)
            ON DUPLICATE KEY UPDATE 
            cache_value = VALUES(cache_value), 
            expire_time = VALUES(expire_time)
            """
            self.db.session.execute(
                db.text(sql),
                {
                    'cache_key': name,
                    'cache_value': value,
                    'expire_time': expire_time
                }
            )
            self.db.session.commit()
        except Exception as e:
            logger.warning("MySQLRedisClient.set " + str(name) + " got exception: " + str(e))
            self.db.session.rollback()

    def setex(self, name: str, time: int | timedelta, value) -> None:
        if not self.db:
            return

        if not isinstance(value, bytes):
            value = (str(value)).encode('utf-8')

        expire = time if isinstance(time, timedelta) else timedelta(seconds=time)
        expire_time = datetime.now() + expire

        try:
            # 使用 INSERT ... ON DUPLICATE KEY UPDATE 避免竞态条件
            sql = """
            INSERT INTO caches (cache_key, cache_value, expire_time) 
            VALUES (:cache_key, :cache_value, :expire_time)
            ON DUPLICATE KEY UPDATE 
            cache_value = VALUES(cache_value), 
            expire_time = VALUES(expire_time)
            """
            self.db.session.execute(
                db.text(sql),
                {
                    'cache_key': name,
                    'cache_value': value,
                    'expire_time': expire_time
                }
            )
            self.db.session.commit()
        except Exception as e:
            logger.warning("MySQLRedisClient.setex " + str(name) + " got exception: " + str(e))
            self.db.session.rollback()

    def setnx(self, name: str, value) -> None:
        if not self.db:
            return

        if not isinstance(value, bytes):
            value = (str(value)).encode('utf-8')

        try:
            # 使用 INSERT IGNORE 避免竞态条件，仅在不存在时插入
            sql = """
            INSERT IGNORE INTO caches (cache_key, cache_value, expire_time) 
            VALUES (:cache_key, :cache_value, :expire_time)
            """
            self.db.session.execute(
                db.text(sql),
                {
                    'cache_key': name,
                    'cache_value': value,
                    'expire_time': None
                }
            )
            self.db.session.commit()
        except Exception as e:
            logger.warning("MySQLRedisClient.setnx " + str(name) + " got exception: " + str(e))
            self.db.session.rollback()

    def delete(self, *names: str) -> None:
        if not self.db or not names:
            return

        try:
            self.db.session.query(Cache).filter(Cache.cache_key.in_(names)).delete(synchronize_session=False)
            self.db.session.commit()
        except Exception as e:
            logger.warning("MySQLRedisClient.delete " + str(names) + " got exception: " + str(e))
            self.db.session.rollback()

    def incr(self, name: str, amount: int = 1) -> bytes:
        if not self.db:
            return b'0'

        try:
            # 使用事务确保原子性，避免并发问题
            with self.db.session.begin():
                # 1. 获取当前值（在事务中）
                current_item = self.db.session.query(Cache).filter(Cache.cache_key == name).first()
                current_value = 0
                if current_item:
                    try:
                        current_value = int(current_item.cache_value.decode('utf-8'))
                    except (ValueError, UnicodeDecodeError):
                        current_value = 0
                
                new_value = current_value + amount
                
                # 2. 原子更新（在同一个事务中）
                if current_item:
                    current_item.cache_value = str(new_value).encode('utf-8')
                else:
                    cache_item = Cache()
                    cache_item.cache_key = name
                    cache_item.cache_value = str(new_value).encode('utf-8')
                    cache_item.expire_time = None
                    self.db.session.add(cache_item)
                
                # 3. 事务自动提交，返回结果
                return str(new_value).encode('utf-8')
                
        except Exception as e:
            logger.warning("MySQLRedisClient.incr " + str(name) + " got exception: " + str(e))
            return b'0'

    def expire(self, name: str, time: int | timedelta) -> None:
        if not self.db:
            return

        expire = time if isinstance(time, timedelta) else timedelta(seconds=time)
        expire_time = datetime.now() + expire

        try:
            # 使用 UPDATE 语句避免竞态条件
            sql = """
            UPDATE caches 
            SET expire_time = :expire_time 
            WHERE cache_key = :cache_key
            """
            result = self.db.session.execute(
                db.text(sql),
                {
                    'cache_key': name,
                    'expire_time': expire_time
                }
            )
            self.db.session.commit()
        except Exception as e:
            logger.warning("MySQLRedisClient.expire " + str(name) + " got exception: " + str(e))
            self.db.session.rollback()

    def zadd(self, name: str, mapping: Mapping) -> None:
        if not self.db:
            return

        try:
            import json

            # 使用事务确保原子性，避免并发问题
            with self.db.session.begin():
                # 1. 在事务中获取现有数据
                cache_item = self.db.session.query(Cache).filter(Cache.cache_key == name).first()
                
                if cache_item:
                    try:
                        existing_data = json.loads(cache_item.cache_value.decode('utf-8'))
                        if not isinstance(existing_data, dict):
                            existing_data = {}
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        existing_data = {}
                    
                    existing_data.update(mapping)
                    cache_item.cache_value = json.dumps(existing_data).encode('utf-8')
                else:
                    cache_item = Cache()
                    cache_item.cache_key = name
                    cache_item.cache_value = json.dumps(dict(mapping)).encode('utf-8')
                    cache_item.expire_time = None
                    self.db.session.add(cache_item)
                
                # 2. 事务自动提交
                
        except Exception as e:
            logger.warning("MySQLRedisClient.zadd " + str(name) + " got exception: " + str(e))

    def zremrangebyscore(self, name: str, min: int | float | str, max: int | float | str):
        if not self.db:
            return 0

        try:
            import json

            # 使用事务确保原子性，避免并发问题
            with self.db.session.begin():
                # 1. 在事务中获取现有数据
                cache_item = self.db.session.query(Cache).filter(Cache.cache_key == name).first()
                if not cache_item:
                    return 0

                try:
                    existing_data = json.loads(cache_item.cache_value.decode('utf-8'))
                    if not isinstance(existing_data, dict):
                        return 0
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return 0

                min_score = float(min) if min != '-inf' else float('-inf')
                max_score = float(max) if max != '+inf' else float('inf')

                members_to_remove = []
                for member, score in existing_data.items():
                    try:
                        score_float = float(score)
                        if min_score <= score_float <= max_score:
                            members_to_remove.append(member)
                    except (ValueError, TypeError):
                        continue

                for member in members_to_remove:
                    del existing_data[member]

                cache_item.cache_value = json.dumps(existing_data).encode('utf-8')
                
                # 2. 事务自动提交，返回结果
                return len(members_to_remove)
                
        except Exception as e:
            logger.warning("MySQLRedisClient.zremrangebyscore " + str(name) + " got exception: " + str(e))
            return 0

    def zcard(self, name: str) -> int:
        if not self.db:
            return 0

        try:
            import json

            cache_item = self.db.session.query(Cache).filter(Cache.cache_key == name).first()
            if not cache_item:
                return 0

            try:
                existing_data = json.loads(cache_item.cache_value.decode('utf-8'))
                if not isinstance(existing_data, dict):
                    return 0
                return len(existing_data)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return 0
        except Exception as e:
            logger.warning("MySQLRedisClient.zcard " + str(name) + " got exception: " + str(e))
            return 0

    def lock(self, name: str, timeout: Optional[float] = None) -> 'MysqlLock':
        return MysqlLock(self.db, name, timeout)


class MysqlLock:
    def __init__(self, db, name: str, timeout: Optional[float] = None):
        self.db = db
        self.name = name
        self.timeout = timeout
        self._locked = False
        logger.info(f"MysqlLock created for {self.name}, timeout={timeout}")
        
    def _cleanup_expired_locks(self) -> None:
        """Clean up expired locks (simple version)"""
        try:
            import json
            import time
            
            current_time = time.time()
            timeout = self.timeout or 60.0
            expire_threshold = current_time - timeout
            
            # Get all lock records
            lock_items = self.db.session.query(Cache).filter(Cache.cache_key.like('lock_%')).all()
            
            expired_items = []
            for item in lock_items:
                try:
                    lock_data = json.loads(item.cache_value.decode('utf-8'))
                    if lock_data.get('timestamp', 0) < expire_threshold:
                        expired_items.append(item)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Corrupted data, mark for deletion
                    expired_items.append(item)
            
            # Delete expired locks
            for item in expired_items:
                self.db.session.delete(item)
            
            if expired_items:
                self.db.session.commit()
                logger.info(f"Cleaned up {len(expired_items)} expired locks")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup expired locks: {str(e)}")
            try:
                self.db.session.rollback()
            except:
                pass

    def acquire(self, blocking: bool = False) -> bool:
        logger.info(f"acquire() called for lock {self.name}")
        if self._locked:
            logger.info(f"Lock {self.name} already acquired, returning True")
            return True

        assert not blocking, "MysqlLock does not support blocking"
        
        # Occasionally clean up expired locks (10% chance to avoid performance impact)
        import random
        if random.random() < 0.1:
            try:
                self._cleanup_expired_locks()
            except Exception as e:
                logger.warning(f"Error during lock cleanup: {str(e)}")
        
        result = self._try_acquire()
        if not result:
            logger.warning(f"Failed to acquire lock {self.name}, timeout={self.timeout}")
        else:
            logger.info(f"Successfully acquired lock {self.name}")
        return result

    def _try_acquire(self) -> bool:
        if not self.db:
            logger.warning(f"Lock {self.name}: db is None")
            return False
        
        logger.info(f"Trying to acquire lock {self.name}")

        try:
            import json
            import time
            import os
            import threading

            lock_key = f"lock_{self.name}"
            current_time = time.time()
            process_id = os.getpid()
            thread_id = threading.get_ident()
            lock_value = {
                "process_id": process_id,
                "thread_id": thread_id,
                "timestamp": current_time
            }

            # Set default timeout if not specified
            timeout = self.timeout or 60.0

            cache_item = self.db.session.query(Cache).filter(Cache.cache_key == lock_key).first()

            if cache_item:
                try:
                    existing_lock = json.loads(cache_item.cache_value.decode('utf-8'))
                    lock_timestamp = existing_lock.get("timestamp", 0)
                    age = current_time - lock_timestamp

                    logger.info(f"Lock {self.name} exists, age={age:.2f}s, timeout={timeout}s")

                    # Check if lock has expired
                    if age > timeout:
                        logger.info(f"Lock {self.name} has expired, trying to acquire")
                        # Lock has expired, try to acquire it atomically
                        result = self.db.session.query(Cache).filter(
                            Cache.cache_key == lock_key,
                            Cache.cache_value == cache_item.cache_value
                        ).update({
                            "cache_value": json.dumps(lock_value).encode('utf-8')
                        })
                        self.db.session.commit()

                        if result > 0:
                            logger.info(f"Successfully acquired expired lock {self.name}")
                            self._locked = True
                            return True
                        else:
                            # Another process updated the lock, try again
                            logger.info(f"Failed to acquire expired lock {self.name}, another process got it")
                            return False
                    else:
                        # Lock is still valid
                        logger.info(f"Lock {self.name} is still valid, cannot acquire")
                        return False
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Corrupted lock data, try to fix it
                    result = self.db.session.query(Cache).filter(
                        Cache.cache_key == lock_key,
                        Cache.cache_value == cache_item.cache_value
                    ).update({
                        "cache_value": json.dumps(lock_value).encode('utf-8')
                    })
                    self.db.session.commit()

                    if result > 0:
                        self._locked = True
                        return True
                    else:
                        return False
            else:
                logger.info(f"No existing lock for {self.name}, creating new one")
                try:
                    cache_item = Cache()
                    cache_item.cache_key = lock_key
                    cache_item.cache_value = json.dumps(lock_value).encode('utf-8')
                    cache_item.expire_time = None
                    self.db.session.add(cache_item)
                    self.db.session.commit()
                    logger.info(f"Successfully created new lock {self.name}")
                    self._locked = True
                    return True
                except Exception as e:
                    # Another process created the lock simultaneously
                    logger.info(f"Failed to create lock {self.name}: {str(e)}")
                    self.db.session.rollback()
                    return False

        except Exception as e:
            logger.error(f"MysqlLock._try_acquire {self.name} got exception: {str(e)}", exc_info=True)
            try:
                self.db.session.rollback()
            except Exception as rollback_e:
                logger.error(f"Failed to rollback transaction: {str(rollback_e)}")
            return False

    def release(self) -> None:
        if not self._locked:
            return

        try:
            import json
            import time
            import os
            import threading

            lock_key = f"lock_{self.name}"
            process_id = os.getpid()
            thread_id = threading.get_ident()

            cache_item = self.db.session.query(Cache).filter(Cache.cache_key == lock_key).first()
            if cache_item:
                try:
                    lock_data = json.loads(cache_item.cache_value.decode('utf-8'))
                    if (lock_data.get("process_id") == process_id and
                        lock_data.get("thread_id") == thread_id):
                        self.db.session.delete(cache_item)
                        self.db.session.commit()
                        logger.info(f"Successfully released lock {self.name}")
                    else:
                        logger.warning(f"Lock {self.name} is owned by another process/thread")
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Corrupted lock data, delete it anyway if it's our lock key
                    logger.warning(f"Corrupted lock data for {self.name}, deleting anyway")
                    self.db.session.delete(cache_item)
                    self.db.session.commit()

            self._locked = False
        except Exception as e:
            logger.warning("MysqlLock.release " + str(self.name) + " got exception: " + str(e))
            self.db.session.rollback()

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"Failed to acquire lock: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def main():
    """Main function to run all MysqlRedisClient tests"""

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import MetaData

    print("Running MysqlRedisClient tests...")

    # Create a Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://user:password@host:port/db_name"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create SQLAlchemy instance
    metadata = MetaData()
    test_db = SQLAlchemy(metadata=metadata)
    test_db.init_app(app)

    # Create client within app context
    with app.app_context():
        client = MysqlRedisClient(test_db)
        client.set_app(app) # Set app context for the client

        try:
            # Test 1: Database connection
            print("Test 1: Database connection")
            assert client.db is not None
            cache_items = client.db.session.query(Cache).all()
            assert isinstance(cache_items, list)
            print("✓ Database connection test passed")

            # Test 2: Pipeline functionality
            print("Test 2: Pipeline functionality")
            pipeline = client.pipeline()
            assert pipeline is client
            print("✓ Pipeline test passed")

            # Test 3: Get non-existent key
            print("Test 3: Get non-existent key")
            result = client.get("nonexistent_key")
            assert result is None
            print("✓ Get non-existent key test passed")

            # Test 4: Set and expire functionality
            print("Test 4: Set and expire functionality")
            client.set("expire_test", "value")
            client.expire("expire_test", 1)
            result = client.get("expire_test")
            assert result == b"value"
            print("✓ Set and expire test passed")

            # Test 5: Setnx with existing key
            print("Test 5: Setnx with existing key")
            client.set("existing_key", "original_value")
            client.setnx("existing_key", "new_value")
            result = client.get("existing_key")
            assert result == b"original_value"
            print("✓ Setnx test passed")

            # Test 6: Incr on non-existent key
            print("Test 6: Incr on non-existent key")
            result = client.incr("new_counter", 10)
            assert result == b"10"
            print("✓ Incr test passed")

            # Test 7: Zadd update
            print("Test 7: Zadd update")
            mapping1 = {"member1": 1.0, "member2": 2.0}
            client.zadd("test_set", mapping1)
            mapping2 = {"member3": 3.0, "member4": 4.0}
            client.zadd("test_set", mapping2)
            card = client.zcard("test_set")
            assert card == 4
            print("✓ Zadd update test passed")

            # Test 8: Background cleanup thread
            print("Test 8: Background cleanup thread")
            assert client._cleanup_thread is not None
            assert client._cleanup_thread.is_alive()
            print("✓ Background cleanup thread test passed")

            # Test 9: Manual cleanup functionality
            print("Test 9: Manual cleanup functionality")
            client.stop_cleanup(sync=False)
            client.set("expired_test_1", "expired_value_1", ex=1)
            client.set("expired_test_2", "expired_value_2", ex=1)
            time.sleep(1)
            cleaned_count = client.cleanup_expired()
            assert cleaned_count >= 2
            print(f"✓ Manual cleanup test passed (cleaned {cleaned_count} entries)")

            print("\n🎉 All MysqlRedisClient tests passed successfully!")

        finally:
            try:
                client.db.session.query(Cache).delete()
                client.db.session.commit()
                print("✓ Test data cleanup completed")
            except Exception as e:
                logger.warning(f"Failed to cleanup test data: {e}")
                client.db.session.rollback()


if __name__ == "__main__":
    main()
