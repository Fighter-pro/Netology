from datetime import datetime, timezone

import aiosqlite
from aiohttp import web


DB_NAME = "advertisements.db"


def validate_advertisement(data, partial=False):
    required_fields = ("title", "description", "owner")

    if not partial:
        for field in required_fields:
            if field not in data:
                raise web.HTTPBadRequest(
                    text=f"Field '{field}' is required"
                )

    for field in required_fields:
        if field in data:
            value = data[field]

            if not isinstance(value, str) or not value.strip():
                raise web.HTTPBadRequest(
                    text=f"Field '{field}' cannot be empty"
                )


async def init_db(app):
    db = await aiosqlite.connect(DB_NAME)
    db.row_factory = aiosqlite.Row

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS advertisements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            owner TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    await db.commit()
    app["db"] = db

    yield

    await db.close()


async def create_advertisement(request):
    data = await request.json()
    validate_advertisement(data)

    created_at = datetime.now(timezone.utc).isoformat()
    db = request.app["db"]

    cursor = await db.execute(
        """
        INSERT INTO advertisements (
            title,
            description,
            owner,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            data["title"].strip(),
            data["description"].strip(),
            data["owner"].strip(),
            created_at,
        ),
    )

    await db.commit()

    ad_id = cursor.lastrowid

    cursor = await db.execute(
        """
        SELECT id, title, description, owner, created_at
        FROM advertisements
        WHERE id = ?
        """,
        (ad_id,),
    )

    advertisement = await cursor.fetchone()

    return web.json_response(
        dict(advertisement),
        status=201,
    )


async def get_advertisement(request):
    ad_id = int(request.match_info["ad_id"])
    db = request.app["db"]

    cursor = await db.execute(
        """
        SELECT id, title, description, owner, created_at
        FROM advertisements
        WHERE id = ?
        """,
        (ad_id,),
    )

    advertisement = await cursor.fetchone()

    if advertisement is None:
        raise web.HTTPNotFound(
            text="Advertisement not found"
        )

    return web.json_response(dict(advertisement))


async def get_all_advertisements(request):
    db = request.app["db"]

    cursor = await db.execute(
        """
        SELECT id, title, description, owner, created_at
        FROM advertisements
        ORDER BY id
        """
    )

    advertisements = await cursor.fetchall()

    return web.json_response(
        [dict(advertisement) for advertisement in advertisements]
    )


async def update_advertisement(request):
    ad_id = int(request.match_info["ad_id"])
    data = await request.json()

    validate_advertisement(data, partial=True)

    db = request.app["db"]

    cursor = await db.execute(
        """
        SELECT id, title, description, owner, created_at
        FROM advertisements
        WHERE id = ?
        """,
        (ad_id,),
    )

    advertisement = await cursor.fetchone()

    if advertisement is None:
        raise web.HTTPNotFound(
            text="Advertisement not found"
        )

    updated = dict(advertisement)

    for field in ("title", "description", "owner"):
        if field in data:
            updated[field] = data[field].strip()

    await db.execute(
        """
        UPDATE advertisements
        SET title = ?, description = ?, owner = ?
        WHERE id = ?
        """,
        (
            updated["title"],
            updated["description"],
            updated["owner"],
            ad_id,
        ),
    )

    await db.commit()

    return web.json_response(updated)


async def delete_advertisement(request):
    ad_id = int(request.match_info["ad_id"])
    db = request.app["db"]

    cursor = await db.execute(
        """
        DELETE FROM advertisements
        WHERE id = ?
        """,
        (ad_id,),
    )

    await db.commit()

    if cursor.rowcount == 0:
        raise web.HTTPNotFound(
            text="Advertisement not found"
        )

    return web.json_response(
        {
            "status": "deleted",
            "id": ad_id,
        }
    )


app = web.Application()
app.cleanup_ctx.append(init_db)

app.add_routes(
    [
        web.post("/advertisements", create_advertisement),
        web.get("/advertisements", get_all_advertisements),
        web.get(
            r"/advertisements/{ad_id:\d+}",
            get_advertisement,
        ),
        web.patch(
            r"/advertisements/{ad_id:\d+}",
            update_advertisement,
        ),
        web.delete(
            r"/advertisements/{ad_id:\d+}",
            delete_advertisement,
        ),
    ]
)


if __name__ == "__main__":
    web.run_app(
        app,
        host="0.0.0.0",
        port=8080,
    )
