import aiosqlite
import sqlite3
import logging


async def init_db():
    async with aiosqlite.connect("quotes.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id TEXT NOT NULL,
                text TEXT NOT NULL,
                UNIQUE(quote_id, text)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS strips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strip_id TEXT NOT NULL,
                link TEXT NOT NULL,
                description TEXT NOT NULL,
                UNIQUE(strip_id, link, description)
                    )
                """)
        logging.getLogger(__name__).info(f"Called/created a database.")
        await db.commit()


async def db_add_quote(quote_id, text):
    async with aiosqlite.connect("quotes.db") as db:
        try:
            await db.execute(
                "INSERT INTO quotes (quote_id, text) VALUES (?, ?)",
                (quote_id, text)
            )
            await db.commit()
            logging.getLogger(__name__).info(f"Added a quote: {quote_id}.")
        except sqlite3.IntegrityError:
            pass


async def db_get_quote(quote_id):
    async with aiosqlite.connect("quotes.db") as db:
        cursor = await db.execute("""
            SELECT text FROM quotes
            WHERE quote_id = ?
        """, (quote_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        logging.getLogger(__name__).info(f"Called a quote: {quote_id}.")
        return row[0]


async def db_add_strip(strip_id, link, desc):
    async with aiosqlite.connect("quotes.db") as db:
        try:
            await db.execute(
                "INSERT INTO strips (strip_id, link, description) VALUES (?, ?, ?)",
                (strip_id, link, desc)
            )
            await db.commit()
            logging.getLogger(__name__).info(f"Added a strip: {strip_id}.")
        except sqlite3.IntegrityError:
            pass

async def db_get_strip(strip_id):
    async with aiosqlite.connect("quotes.db") as db:
        cursor = await db.execute("""
            SELECT link, description FROM strips
            WHERE strip_id = ?
        """, (strip_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        link, desc = row
        logging.getLogger(__name__).info(f"Called a strip: {strip_id}.")
        return link, desc