// src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { format, parseISO, startOfWeek, addDays } from 'date-fns';

type Showtime = {
  title: string;
  year: number;
  theater: string;
  tags: string[];
  datetime: string; // ISO date string
};

export default function HomePage() {
  const [showtimes, setShowtimes] = useState<Showtime[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedTheater, setSelectedTheater] = useState<string | null>(null);

  const uniqueTags = [...new Set(showtimes.flatMap(s => s.tags))];
  const uniqueTheaters = [...new Set(showtimes.map(s => s.theater))];

  useEffect(() => {
    // Fetch data from the API route
    fetch('/api/showtimes')
      .then(res => res.json())
      .then(data => setShowtimes(data))
      .catch(err => console.error('Failed to fetch showtimes:', err));
  }, []);

  const startOfThisWeek = startOfWeek(new Date(), { weekStartsOn: 1 }); // Monday
  const daysOfWeek = Array.from({ length: 7 }, (_, i) => addDays(startOfThisWeek, i));

  const filtered = showtimes.filter(show => {
    const tagMatch = selectedTags.length === 0 || selectedTags.every(tag => show.tags.includes(tag));
    const theaterMatch = !selectedTheater || show.theater === selectedTheater;
    return tagMatch && theaterMatch;
  });

  const groupedByDay = daysOfWeek.map(day => {
    const dateKey = format(day, 'yyyy-MM-dd');
    const matches = filtered.filter(show => {
        return show.datetime && format(parseISO(show.datetime), 'yyyy-MM-dd') === dateKey;
    });

    // Group by film within each day
    const films = matches.reduce((acc, show) => {
        const filmKey = `${show.title}-${show.year}`;
        if (!acc[filmKey]) {
            acc[filmKey] = {
                title: show.title || "Untitled",
                year: show.year || "No Year",
                theater: show.theater,
                showtimes: [],
                tags: show.tags || []
            };
        }
        acc[filmKey].showtimes.push(show.datetime);
        return acc;
    }, {});

    return {
        date: day,
        films: Object.values(films)
    };
  });

  const toggleTag = (tag: string) => {
    setSelectedTags(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6">This Week's Showtimes</h1>

      <div className="mb-4">
        <h2 className="font-semibold">Filter by Theater:</h2>
        <div className="flex gap-2 mt-2">
          {uniqueTheaters.map(theater => (
            <button
              key={theater}
              className={`px-3 py-1 rounded-full border ${selectedTheater === theater ? 'bg-blue-500 text-white' : 'bg-white'}`}
              onClick={() => setSelectedTheater(selectedTheater === theater ? null : theater)}
            >
              {theater}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-4">
        <h2 className="font-semibold">Filter by Tags:</h2>
        <div className="flex gap-2 mt-2 flex-wrap">
          {uniqueTags.map(tag => (
            <button
              key={tag}
              className={`px-3 py-1 rounded-full border ${selectedTags.includes(tag) ? 'bg-green-500 text-white' : 'bg-white'}`}
              onClick={() => toggleTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {groupedByDay.map(({ date, films }) => (
        <div key={date.toISOString()} className="mb-6">
          <h2 className="text-xl font-semibold mb-2">{format(date, 'EEEE, MMM d')}</h2>
          {films.length === 0 ? (
            <p className="text-gray-500">No showtimes</p>
          ) : (
            <div className="grid gap-4">
              {films.map((film, idx) => (
                <div key={`${film.title}-${film.year}`} className="p-4 bg-white shadow rounded-xl">
                  <h3 className="text-1xl font-bold mb-2">{film.title} ({film.year})</h3>
                  <p className="text-sm text-gray-500">{film.theater}</p>
                  <div className="mt-1 text-sm">
                    {film.showtimes.map((time, i) => format(parseISO(time), 'h:mm a')).join(', ')}
                  </div>
                  <div className="mt-1 text-sm text-gray-600">
                    {films.tags ? film.tags.join(', ') : ""}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
