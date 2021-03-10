from aiohttp import web
import asyncio
from aio_pika import connect_robust, Message, DeliveryMode, ExchangeType


async def init_pika(app):
    loop = asyncio.get_event_loop()
    rmq_url = app['rmq']['url']
    connection = await connect_robust(
        url=rmq_url, loop=loop
    )
    channel = await create_channel(connection)
    app['rmq']['connection'] = connection
    app['rmq']['channel'] = channel
    app['rmq']['exchange'] = await create_exchange(channel)


async def create_channel(connection):
    channel = await connection.channel()
    return channel


async def create_exchange(channel):
    hello_exchange = await channel.declare_exchange(
        'hello_exchange', ExchangeType.DIRECT, durable=True
    )
    queue = await channel.declare_queue("hello_queue", durable=True)
    await queue.bind(hello_exchange, routing_key="hello_queue")
    return hello_exchange


async def close_pika(app):
    connection = app['rmq']['connection']
    await connection.close()


def setup_pika(app, rmq_url):
    app['rmq'] = {}
    app['rmq'].update({'url': rmq_url})
    app.on_startup.append(init_pika)
    app.on_cleanup.append(close_pika)


async def send_handler(request):
    message = {'message': 'Hello world'}
    exchange = request.app['rmq']['exchange']

    await exchange.publish(
        Message(b"Hello World!", delivery_mode=DeliveryMode.PERSISTENT),
        routing_key="hello_queue"
    )
    return web.json_response(message)


async def reload_handler(request):
    channel = request.app['rmq']['channel']
    if channel.is_closed:
        await init_pika(request.app)
        channel = request.app['rmq']['channel']

    return web.json_response({'message': 'done', 'channel_closed': channel.is_closed})


async def init_app():
    app = web.Application()
    setup_pika(app, 'amqp://admin:adminsecret@192.168.10.1/hello')
    app.router.add_route('GET', '/send', send_handler)
    app.router.add_route('GET', '/reload', reload_handler)

    return app


def main():
    app = init_app()
    web.run_app(app)


if __name__ == "__main__":
    main()
