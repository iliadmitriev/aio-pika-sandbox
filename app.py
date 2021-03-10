from aiohttp import web
import asyncio
from aio_pika import connect, Message


async def init_pika(app):
    loop = asyncio.get_event_loop()
    rmq_url = app['rmq_url']
    connection = await connect(
        url=rmq_url, loop=loop
    )
    app['connection'] = connection
    app['channel'] = await create_channel(connection)


async def create_channel(connection):
    channel = await connection.channel()
    return channel


async def close_pika(app):
    connection = app['connection']
    await connection.close()


def setup_pika(app, rmq_url):
    app['rmq_url'] = rmq_url
    app.on_startup.append(init_pika)
    app.on_cleanup.append(close_pika)


async def send_handler(request):
    message = {'message': 'Hello world'}
    channel = request.app['channel']
    await channel.default_exchange.publish(
        Message(b"Hello World!"),
        routing_key="hello",
    )
    return web.json_response(message)


async def init_app():
    app = web.Application()
    setup_pika(app, 'amqp://admin:adminsecret@192.168.10.1/hello')
    app.router.add_route('GET', '/send', send_handler)
    return app


def main():
    app = init_app()
    web.run_app(app)


if __name__ == "__main__":
    main()
