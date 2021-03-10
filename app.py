from aiohttp import web
import asyncio
from aio_pika import connect, Message, DeliveryMode


async def init_pika(app):
    loop = asyncio.get_event_loop()
    rmq_url = app['rmq']['url']
    connection = await connect(
        url=rmq_url, loop=loop
    )
    app['rmq']['connection'] = connection
    app['rmq']['channel'] = await create_channel(connection)


async def create_channel(connection):
    channel = await connection.channel()
    queue = await channel.declare_queue("hello_queue", durable=True)
    return channel


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
    channel = request.app['rmq']['channel']
    await channel.default_exchange.publish(
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
