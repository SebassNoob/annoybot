import libsql_client


async def create_client():
    url = "ws://localhost:8080"
    client = libsql_client.create_client(url)
    return client
