// src/app/page.tsx
'use client';

import { useState } from 'react';

const movies = [
  {
    id: 1,
    title: "The Green Ray",
    theater: "Roxy",
    tags: ["Drama", "French"],
    showtimes: ["7:00 PM", "9:30 PM"],
  },
  {
    id: 2,
    title: "Stop Making Sense",
    theater: "Alamo",
    tags: ["Documentary", "Music"],
    showtimes: ["6:00 PM", "8:15 PM"],
  },
  {
    id: 3,
    title: "Fallen Leaves",
    theater: "Roxy",
    tags: ["Drama", "Comedy"],
    showtimes: ["5:00 PM", "7:15 PM"],
  },
];

const uniqueTags = [...new Set(movies.flatMap(m => m.tags))];
const uniqueTheaters = [...new Set(movies.map(m => m.theater))];

export default function HomePage() {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedTheater, setSelectedTheater] = useState<string | null>(null);

  const filteredMovies = movies.filter(movie => {
    const tagMatch = selectedTags.length === 0 || selectedTags.every(tag => movie.tags.includes(tag));
    const theaterMatch = !selectedTheater || movie.theater === selectedTheater;
    return tagMatch && theaterMatch;
  });

  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6">Now Playing</h1>

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

      <div className="grid gap-4">
        {filteredMovies.map(movie => (
          <div key={movie.id} className="p-4 bg-white shadow rounded-xl">
            <h3 className="text-xl font-bold">{movie.title}</h3>
            <p className="text-sm text-gray-500">{movie.theater}</p>
            <div className="mt-2 text-sm">Tags: {movie.tags.join(", ")}</div>
            <div className="mt-1 text-sm">Showtimes: {movie.showtimes.join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
