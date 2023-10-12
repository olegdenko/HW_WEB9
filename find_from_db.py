import docker
import re
import redis
import time

from models import Author, Quote
from connection import connect, client

import platform
is_windows = platform.system() == "Windows"

if is_windows:
    client = docker.DockerClient(base_url='tcp://localhost:2375')
    client.containers.run(
        'redis:latest', name='my-redis-container', detach=True, ports={'6379/tcp': 6379})
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
else:
    def start_redis_container():
        client = docker.from_env()
        time.sleep(4)
        try:
            container = client.containers.get('my-redis-container')
            if container.status != 'running':
                container.start()
        except docker.errors.NotFound:
            client.containers.run(
                'redis:latest', name='my-redis-container', detach=True, ports={'6379/tcp': 6379})

    start_redis_container()
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def search_by_name(name):
    regex = re.compile(f"^{name}.*", re.IGNORECASE)
    authors = Author.objects(fullname=regex)
    if authors:
        results = []
        for author in authors:
            quotes = Quote.objects(author=author)
            author_quotes = [
                f"Цитата: {quote.quote}\nАвтор: {quote.author.fullname}\nТеги: {', '.join(quote.tags)}"
                for quote in quotes
            ]
            results.extend(author_quotes)
        return "\n".join(results)
    else:
        return "Автор не знайдений"


def search_by_tag(tag):
    regex = re.compile(f"^{tag}.*", re.IGNORECASE)
    quotes = Quote.objects(tags__in=[regex])
    if quotes:
        results = [
            f"Цитата: {quote.quote}\nАвтор: {quote.author.fullname}\nТеги: {', '.join(quote.tags)}"
            for quote in quotes
        ]
        return "\n".join(results)
    else:
        return "Цитати не знайдені"


def main():
    while True:
        command = input("Введіть команду: ").strip()
        match = re.match(r"(name|tag):(.+)", command)

        if match:
            option, value = match.groups()
            if option == "name":
                short_name_match = re.match(r"^(\w{2,})", value)
                if short_name_match:
                    name = short_name_match.group(1)
                    result = search_by_name(name)
                else:
                    pass
            elif option == "tag":
                short_tag_match = re.match(r"^(\w{2,})", value)
                if short_tag_match:
                    tag = short_tag_match.group(1)
                    result = search_by_tag(tag)
                else:
                    pass
            print(result)
        elif command == "exit":
            container = client.containers.get('my-redis-container')
            container.stop()
            container.remove()
            client.close()
            break
        else:
            print("Невідома команда")
            continue

if __name__ == "__main__":
    main()
