import { NextResponse } from 'next/server';
import mysql from 'mysql2/promise';
import { startOfWeek, addDays, formatISO } from 'date-fns';

export async function GET() {
  try {
    const pool = mysql.createPool({
      host: 'localhost',
      user: 'root',
      password: 'yos',
      database: 'movieDB',
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0,
    });

    const start = formatISO(startOfWeek(new Date(), { weekStartsOn: 1 }));
    const end = formatISO(addDays(new Date(), 7));

    const [rows] = await pool.query(
      `SELECT Title as title,
      COALESCE(Year, 0) as year,
      Showtime AS datetime,
      Theater as theater
      FROM
      (
      SELECT *, 'Musicbox' as Theater FROM musicbox_showtimes
      UNION
      SELECT *, 'Siskel' as Theater FROM siskel_showtimes
      ) as showdies
      WHERE Showtime >= ? and Showtime < ?
      ORDER BY Showtime ASC;`,
      [start, end]
    );

    // console.log("📝 Raw SQL Results:", rows);

    await pool.end();

    const formatted = (rows as any[]).map(row => ({
      ...row,
      tags: [], // Placeholder for tags. Will create these soon
      // datetime: row.datetime ? new Date(row.datetime.replace(" ", "T")).toISOString() : null,
      datetime: row.datetime instanceof Date
        ? row.datetime.toISOString()
        : row.datetime
          ? new Date(row.datetime.replace(" ", "T")).toISOString()
          : null,
    }));

    return NextResponse.json(formatted);
  } catch (err) {
    console.error("💥 SQL Error:", err);
    return NextResponse.json({ error: 'DB error' }, { status: 500 });
  }
}

  // const [rows] = await pool.query(`
    //   SELECT
    //     id,
    //     title,
    //     theater,
    //     tags,
    //     showtimes
    //   FROM showtimes
    // `);
    
    // // Optional: Parse tags and showtimes if stored as CSV in DB
    // const parsed = (rows as any[]).map(row => ({
    //   ...row,
    //   tags: row.tags ? row.tags.split(',') : [],
    //   showtimes: row.showtimes ? row.showtimes.split(',') : [],
    // }));

    // return NextResponse.json(parsed);
