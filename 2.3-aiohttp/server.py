from aiohttp import web
from datetime import datetime, timezone

app = web.Application()

advertisements = {}
next_id = 1


async def create_advertisement(request):
    global next_id

    data = await request.json()

    required_fields = ("title", "description", "owner")
    for field in required_fields:
        if not data.get(field):
            raise web.HTTPBadRequest(
                text=f"Field '{field}' is required"
            )

    advertisement = {
        "id": next_id,
        "title": data["title"],
        "description": data["description"],
        "owner": data["owner"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    advertisements[next_id] = advertisement
    next_id += 1

    return web.json_response(advertisement, status=201)


async def get_advertisement(request):
    ad_id = int(request.match_info["ad_id"])

    advertisement = advertisements.get(ad_id)

    if advertisement is None:
        raise web.HTTPNotFound(text="Advertisement not found")

    return web.json_response(advertisement)


async def update_advertisement(request):
    ad_id = int(request.match_info["ad_id"])

    advertisement = advertisements.get(ad_id)

    if advertisement is None:
        raise web.HTTPNotFound(text="Advertisement not found")

    data = await request.json()

    for field in ("title", "description", "owner"):
        if field in data:
            advertisement[field] = data[field]

    return web.json_response(advertisement)


async def delete_advertisement(request):
    ad_id = int(request.match_info["ad_id"])

    advertisement = advertisements.pop(ad_id, None)

    if advertisement is None:
        raise web.HTTPNotFound(text="Advertisement not found")

    return web.json_response({
        "status": "deleted",
        "id": ad_id
    })


async def get_all_advertisements(request):
    return web.json_response(list(advertisements.values()))


app.add_routes([
    web.post("/advertisements", create_advertisement),
    web.get("/advertisements", get_all_advertisements),
    web.get("/advertisements/{ad_id}", get_advertisement),
    web.patch("/advertisements/{ad_id}", update_advertisement),
    web.delete("/advertisements/{ad_id}", delete_advertisement),
])


if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
