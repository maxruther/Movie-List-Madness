import { NextResponse } from 'next/server';
import mysql from 'mysql2/promise';

// You'll want to use environment variables in production!
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'yos',
  database: 'movieDB',
});

export async function GET() {
  try {
    const [rows] = await pool.query(`
    SELECT i.Metascore, i.\`Title Searched\`, i.\`Year Searched\`, i.\`Director Searched\`, s.Theater, max(s.Showtime_Date), min(s.Showtime_Date) FROM
        (
        SELECT * FROM siskel_show_info_mc_info
        UNION
        SELECT * FROM musicbox_show_info_mc_info
        ) as i
    INNER JOIN
        (
        SELECT *, 'Siskel' as Theater FROM siskel_showtimes
        UNION
        SELECT *, 'Musicbox' as Theater FROM musicbox_showtimes_2
        ) as s
    ON s.\`Title\`=i.\`Title Searched\` and
    s.\`Year\`=i.\`Year Searched\` and
    s.\`Director\`=i.\`Director Searched\`
    GROUP BY i.Metascore, i.\`Title Searched\`, i.\`Year Searched\`, i.\`Director Searched\`, s.Theater
    ORDER BY i.Metascore DESC, max(s.Showtime_Date) DESC
    `);
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
  } catch (error) {
    console.error('MySQL fetch error:', error);
    return NextResponse.json({ error: 'Database query failed' }, { status: 500 });
  }
}
