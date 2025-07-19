// src/app/page.tsx
'use client';

import { useEffect, useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { parse, format, startOfWeek, getDay, addDays } from 'date-fns';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { match } from 'assert';

const locales = {
  'en-US': require('date-fns/locale/en-US')
};

type Showtime = {
  title: string;
  year: number;
  director: string;
  start: string | Date;
  end: string | Date;
  runtime: number;
  link: string;
  description: string;
  theater: string;
};

const localizer = dateFnsLocalizer({
  format,
  parse: (value, formatString, locale) => parse(value, formatString, new Date(), { locale }),
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
});

function EventComponent({ event }: { event: Showtime }) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState<{ top: number; left: number }>({ top: 0, left: 0 });

  useEffect(() => {
    const textEl = textRef.current;
    const wrapperEl = wrapperRef.current;
    if (textEl && wrapperEl) {
      const textHeight = textEl.scrollHeight;
      const containerHeight = wrapperEl.offsetHeight;
      if (textHeight > containerHeight) {
        setScale(containerHeight / textHeight);
      } else {
        setScale(1);
      }
    }
  }, [event.title]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (!wrapperRef.current?.contains(e.target as Node)) {
        setShowTooltip(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  const bringToFront = (e: React.MouseEvent) => {
    e.stopPropagation();
    const rect = wrapperRef.current?.getBoundingClientRect();
    if (!rect) return;
    setTooltipPosition({ top: rect.bottom + window.scrollY + 6, left: rect.left + window.scrollX });
    setShowTooltip(true);

    const eventNode = wrapperRef.current?.closest('.rbc-event');
    if (eventNode instanceof HTMLElement) {
      eventNode.style.zIndex = '9999';
      eventNode.style.position = 'relative';

      setTimeout(() => {
        eventNode.style.zIndex = 'auto';
        eventNode.style.position = 'absolute';
      }, 3000);
    }
  };

  const formatTime = (date: Date) => date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  const formatDate = (date: Date) => date.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });

  return (
    <div
      ref={wrapperRef}
      onClick={bringToFront}
      style={{
        backgroundColor: event.theater === 'Music Box' ? '#b91c1c' : '#1e3a8a',
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'flex-start',
        border: 'none',
        boxShadow: 'none',
        pointerEvents: 'auto',
        position: 'relative'
      
      }}
    >
      <div
        ref={textRef}
        style={{
          fontSize: `${0.85 * scale}rem`,
          lineHeight: '1.2',
          wordWrap: 'break-word',
          whiteSpace: 'normal',
          width: '100%',
          color: 'white'
        }}
      >
        {event.title}
      </div>

      {showTooltip && createPortal(
        <div
          style={{
            position: 'absolute',
            top: tooltipPosition.top,
            left: tooltipPosition.left,
            backgroundColor: 'white',
            color: '#333',
            border: '1px solid #ccc',
            borderRadius: '6px',
            fontSize: '0.8rem',
            zIndex: 10000,
            minWidth: '180px',
            padding: '8px',
            boxShadow: '0px 4px 6px rgba(0,0,0,0.1)'
          }}
        >
          <strong>{event.title}</strong>
          <div>{formatDate(new Date(event.start))}</div>
          <div>{formatTime(new Date(event.start))} – {formatTime(new Date(event.end))}</div>
          <div>{event.year}</div>
          <div>{event.theater}</div>
        </div>,
        document.body
      )}
    </div>
  );
}

export default function HomePage() {
  const [events, setEvents] = useState<Showtime[]>([]);
  const [currentDate, setCurrentDate] = useState(new Date());

  const allTheaters = ["Music Box", "Siskel"];
  const [selectedTheaters, setSelectedTheaters] = useState(new Set(allTheaters));

  const allSelected = allTheaters.every(theater => selectedTheaters.has(theater));

  type MetaReportRow = {
    metascore: number;
    title: string;
    year: number;
    director: string;
    theaters: string;
    first_screen_day: string;
    last_screen_day: string
  }

  const [metaReport, setMetaReport] = useState<MetaReportRow[]>([]);

  const handleCheckboxChange = (theater: string) => {
    setSelectedTheaters(prev => {
      const updated = new Set(prev);
      if (updated.has(theater)) {
        updated.delete(theater);
      } else {
        updated.add(theater);
      }
      return updated;
    });
  };

  const handleSelectAllChange = () => {
    setSelectedTheaters(prev => {
      if (allSelected) {
        return new Set();
      } else {
        return new Set(allTheaters);
      }
    });
  };

  const [originalEvents, setOriginalEvents] = useState<Showtime[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<Showtime[]>([]);
  const [highlightedTitles, setHighlightedTitles] = useState<Set<string>>(new Set());
  const [highlightedDirectors, setHighlightedDirectors] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch('/api/showtimes');
        const data = await res.json();

        const parsedEvents = data.flatMap((event: Showtime) => {
          const start = new Date(event.start);
          const end = new Date(event.end);

          const sameDay = start.toDateString() === end.toDateString();
          if (sameDay) {
            return {
              ...event,
              start,
              end,
            };
          } else {
            const splitEnd = new Date(start);
            splitEnd.setHours(23, 59, 59, 999);

            const nextStart = new Date(splitEnd);
            nextStart.setDate(nextStart.getDate() + 1);
            nextStart.setHours(0, 0, 0, 0);

            return [
              {
                ...event,
                start,
                end: splitEnd,
              },
              {
                ...event,
                start: nextStart,
                end,
              },
            ];
          }
        });

        setOriginalEvents(parsedEvents);
        setFilteredEvents(parsedEvents);
      } catch (error) {
        console.error("Failed to fetch showtimes:", error);
      }
    };

    fetchEvents();


    const fetchMeta = async () => {
      try {
        const res = await fetch('/api/metascore-report');
        const data = await res.json();
        setMetaReport(data);
      } catch (err) {
        console.error("Failed to load the metascore report: ", err);
      }
    };

    fetchMeta();
  }, []);

  const handleTitleClick = (title: string) => {
    const updated = new Set(highlightedTitles);
    if (highlightedTitles.has(title)) {
      updated.delete(title);
    } else {
      updated.add(title);
    }
    setHighlightedTitles(updated);
    filterEvents(updated, highlightedDirectors);
  };

  const handleDirectorClick = (director: string) => {
    const updated = new Set(highlightedDirectors);
    if (highlightedDirectors.has(director)) {
      updated.delete(director);
    } else {
      updated.add(director);
    }
    setHighlightedDirectors(updated);
    filterEvents(highlightedTitles, updated);
  };

  const clearFilters = () => {
    setFilteredEvents(originalEvents);
    setHighlightedTitles(new Set());
    setHighlightedDirectors(new Set());
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      const timeGrid = document.querySelector('.rbc-time-content');
      if (timeGrid instanceof HTMLElement) {
        timeGrid.scrollTop = timeGrid.scrollHeight;
      }
    }, 0);
    return () => clearTimeout(timer);
  }, [currentDate, filteredEvents]);

  const filterEvents = (titles: Set<string>, directors: Set<string>) => {
    const hasTitleFilter = titles.size > 0;
    const hasDirectorFilter = directors.size > 0;

    const filtered = originalEvents.filter(event => {
      const matchTitle = titles.has(event.title);
      const matchDirector = directors.has(event.director);

      if (hasTitleFilter && hasDirectorFilter) {
        return matchTitle || matchDirector;
      } else if (hasTitleFilter) {
        return matchTitle;
      } else if (hasDirectorFilter) {
        return matchDirector;
      } else {
        return true;
      }
    });

    setFilteredEvents(filtered);
  };

  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 })
  const weekEnd = addDays(weekStart, 6);

  const weeklyMeta = metaReport.filter(row => {
    const first = new Date(row.first_screen_day);
    const last = new Date(row.last_screen_day);
    return first <= weekEnd && last >= weekStart;
  })

  return (
    <div className="h-screen flex flex-col bg-gray-100 p-4 md:p-6">
      <h1 className="text-2xl md:text-3xl font-bold mb-4 md:mb-6">Weekly Indie Showtimes</h1>

      <div className="mb-4">
        <div style={{ marginBottom: "0.5rem", fontWeight: "bold" }}>Theater Selection:</div>
          <label style={{ marginRight: "1rem", fontStyle: "italic", color: "#333" }}>
            <input
              type="checkbox"
              checked={allSelected}
              onChange={handleSelectAllChange}
            />{' '}
            Select all theaters
          </label>
          {allTheaters.map(theater => (
            <label key={theater} style={{ marginRight: "1rem" }}>
              <input
                type="checkbox"
                checked={selectedTheaters.has(theater)}
                onChange={() => handleCheckboxChange(theater)}
              />
              {theater}
            </label>
          ))}
      </div>
      
      <div className="flex flex-col md:flex-row gap-6 flex-grow overflow-hidden">
        <div className="flex-grow md:w-2/3 overflow-hidden min-h-0">
          <Calendar
            localizer={localizer}
            events={filteredEvents.filter(event => selectedTheaters.has(event.theater))}
            startAccessor="start"
            endAccessor="end"
            style={{ height: '100%' }}
            defaultView="week"
            views={['week', 'day']}
            step={60}
            timeslots={1}
            min={new Date(1970, 0, 1, 0, 0)}
            max={new Date(1970, 0, 1, 23, 59)}
            date={currentDate}
            onNavigate={(newDate) => {
              setCurrentDate(newDate);
              setHighlightedTitles(new Set());
              setHighlightedDirectors(new Set());
              setFilteredEvents(originalEvents);
            }}
            onView={(newView) => {
              clearFilters();
            }}
            components={{
              event: EventComponent
            }}
            eventPropGetter={(event) => {
              const isHighlighted =
              (highlightedTitles.has(event.title)) ||
              (highlightedDirectors.has(event.director));

              const backgroundColor = event.theater === 'Music Box' ? '#b91c1c' : '#1e3a8a';
              const style = {
                backgroundColor,
                color: 'white',
                border: isHighlighted
                  ? '3px solid gold'
                  : '2px solid rgba(255, 255, 255, 0.4)'
              };
              return { style };
            }}
          ></Calendar>
        </div>

        <div className="md:w-1/3 flex flex-col min-h-0">
          {/* 🔹 Weekly Metascore Report */}
          {weeklyMeta.length > 0 && (
            <div className="mt-8 bg-white p-4 rounded shadow flex flex-col flex-grow min-h-0">
              <h2 className="text-xl font-semibold mb-2">This Week’s Critic Picks</h2>
              <div className="flex items-center flex-wrap gap-2 mb-3">
                {[...highlightedTitles].map((title) => (
                  <span
                  key={title}
                  className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full cursor-pointer flex items-center gap-1"
                  onClick={() => {
                    const updated = new Set(highlightedTitles);
                    updated.delete(title);
                    setHighlightedTitles(updated);
                    filterEvents(updated, highlightedDirectors);
                  }}
                  >
                    Title: {title} <span className="ml-1 text-blue-500 hover:text-blue-700">x</span>
                  </span>
                ))}
                {[...highlightedDirectors].map((director) => (
                  <span
                  key={director}
                  className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full cursor-pointer flex items-center gap-1"
                  onClick={() => {
                    const updated = new Set(highlightedDirectors);
                    updated.delete(director);
                    setHighlightedDirectors(updated);
                    filterEvents(highlightedTitles, updated);
                  }}
                >
                  Director: {director} <span className="ml-1 text-purple-500 hover:text-purple-700">×</span>
                </span>
                ))}
                <button
                  className="px-3 py-1 text-sm text-white bg-gray-700 rounded hover:bg-gray-600"
                  onClick={clearFilters}
                >
                  Clear filter
                </button>
              </div>
              <div className="flex-grow overflow-y-auto min-h-0">
                <table className="table-auto w-full text-xs leading-snug max-h-full overflow-hidden">
                  <thead className="sticky top-0 bg-white z-10">
                    <tr className="bg-gray-200">
                      <th className="px-1 py-0.5 text-left">🎯 Metascore</th>
                      <th className="px-1 py-0.5 text-left">🎬 Title</th>
                      <th className="px-1 py-0.5 text-left">📅 Year</th>
                      <th className="px-1 py-0.5 text-left">🎞️ Director</th>
                      <th className="px-1 py-0.5 text-left">🏛️ Theater</th>
                    </tr>
                  </thead>
                  <tbody>
                    {weeklyMeta.map((row, idx) => (
                      <tr key={idx} className="border-t">
                        <td className="px-1 py-0.5">{(row.metascore * 100).toFixed(0)}</td>
                        <td
                          className="px-1 py-0.5 text-blue-600 underline cursor-pointer"
                          onClick={() => handleTitleClick(row.title)}
                        >
                          {row.title}
                        </td>
                        <td className="px-1 py-0.5">{row.year}</td>
                        <td
                          className="px-1 py-0.5 text-purple-600 underline cursor-pointer"
                          onClick={() => handleDirectorClick(row.director)}
                        >
                          {row.director}
                        </td>
                        <td className="px-1 py-0.5">{row.theaters}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
