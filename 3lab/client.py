import asyncio
import websockets
import aiohttp
import json
import argparse

async def create_user(username):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/users/",
            json={"username": username}
        ) as response:
            return await response.json()

async def create_task(user_id, url, max_depth):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://localhost:8000/tasks/{user_id}",
            json={"url": url, "max_depth": max_depth}
        ) as response:
            return await response.json()

async def websocket_client(user_id):
    uri = f"ws://localhost:8000/ws/{user_id}?token=secret_token"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to WebSocket for user {user_id}")
            async for message in websocket:
                print(f"Received message: {message}")
    except Exception as e:
        print(f"WebSocket error: {e}")

async def execute_command(cmd, args):
    try:
        if cmd == "create_user":
            username = args[0]
            result = await create_user(username)
            print(result)
        elif cmd == "create_task":
            user_id = int(args[0])
            url = args[1]
            max_depth = int(args[2])
            result = await create_task(user_id, url, max_depth)
            print(result)
        elif cmd == "ws":
            user_id = int(args[0])
            await websocket_client(user_id)
        else:
            print(f"Неизвестная команда: {cmd}")
    except Exception as e:
        print(f"Ошибка: {e}")

async def interactive_mode():
    print("Консольный клиент. Команды: create_user, create_task, ws, exit")
    while True:
        command = input("> ").strip().split()
        if not command:
            continue
        cmd = command[0]
        args = command[1:]
        if cmd == "exit":
            break
        await execute_command(cmd, args)

async def run_script(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            command = line.split()
            cmd = command[0]
            args = command[1:]
            print(f"Executing: {line}")
            await execute_command(cmd, args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", help="Путь к файлу со скриптом")
    args = parser.parse_args()

    if args.script:
        asyncio.run(run_script(args.script))
    else:
        asyncio.run(interactive_mode())