// src/app/api/metascore-report/route.ts
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
            `SELECT * FROM metascore_report`
        );

        // console.log("📝 Raw SQL Results:", rows);

        // Format the rows for the calendar
        const events = rows
            .map(row => {
                return {
                    id: `${row.title}_${row.year}_${row.director}_${row.theaters}`,
                    
                    metascore: row.metascore,
                    title: row.title,
                    year: row.year,
                    director: row.director,
                    theaters: row.theaters || 'Unknown Theater',
                    first_screen_day: row.first_screen_day,
                    last_screen_day: row.last_screen_day,
                };
            })
            .filter(Boolean);

        await pool.end();
        return NextResponse.json(events);
    } catch (error) {
        console.error('Error fetching metascore-report:', error);
        return NextResponse.json({ error: 'Failed to fetch metascore-report' }, { status: 500 });
    }
}
