// src/app/api/showtimes/route.ts
import mysql from 'mysql2/promise';
import { NextResponse } from 'next/server';

export async function GET() {
    try {
        // Establish a connection to the MySQL database
        const pool = await mysql.createPool({
            host: 'localhost',
            user: 'root',
            password: 'yos',
            database: 'movieDB',
            waitForConnections: true,
            connectionLimit: 10,
            queueLimit: 0
        });

        // Query the database for showtimes within the next week
        const [rows] = await pool.query(
            `SELECT * FROM v_screenings_enriched`

            // // OLD QUERY:
            // `SELECT Title AS title,
            // COALESCE(Year, 0) AS year,
            // Showtime AS start,
            // Theater as theater
            // FROM 
            // (
            // SELECT *, 'Musicbox' as Theater FROM musicbox_showtimes
            // UNION
            // SELECT *, 'Siskel' as Theater FROM siskel_showtimes
            // ) as showdies
            //  ORDER BY Showtime ASC`
            //  WHERE Showtime >= NOW() AND Showtime < DATE_ADD(NOW(), INTERVAL 7 DAY)
        );

        // console.log("📝 Raw SQL Results:", rows);

        // Format the rows for the calendar
        const events = rows
            .map(row => {
                // Handle datetime conversion safely
                const startDate = typeof row.start === 'string'
                    ? new Date(row.start.replace(" ", "T"))
                    : row.start instanceof Date
                    ? row.start
                    : null;

                if (!startDate || isNaN(startDate.getTime())) {
                    console.error("Invalid date in row:", row);
                    return null; // Skip this row if the date is invalid
                }

                const endDate = new Date(startDate.getTime() + row.runtime * 60 * 1000);


                return {
                    id: `${row.title}_${startDate.toISOString()}_${row.theater}`,
                    
                    title: row.title,
                    year: row.year,
                    director: row.director,
                    description: row.description,
                    link: row.link,

                    start: startDate,
                    end: endDate,

                    theater: row.theater || 'Unknown Theater'
                };
            })
            .filter(Boolean);

        await pool.end();
        return NextResponse.json(events);
    } catch (error) {
        console.error('Error fetching showtimes:', error);
        return NextResponse.json({ error: 'Failed to fetch showtimes' }, { status: 500 });
    }
}
