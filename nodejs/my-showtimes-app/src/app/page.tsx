// src/app/page.tsx
'use client';

import { useEffect, useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { parse, format, startOfWeek, getDay } from 'date-fns';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const locales = {
  'en-US': require('date-fns/locale/en-US')
};

type Showtime = {
  title: string;
  year: number;
  start: string | Date;
  end: string | Date;
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
        backgroundColor: event.theater === 'Musicbox' ? '#b91c1c' : '#1e3a8a',
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

  const allTheaters = ["Musicbox", "Siskel"];
  const [selectedTheaters, setSelectedTheaters] = useState(new Set(allTheaters));

  const allSelected = allTheaters.every(theater => selectedTheaters.has(theater));

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

        console.log("🎥 Parsed showtimes:", parsedEvents);
        setEvents(parsedEvents);
      } catch (error) {
        console.error("Failed to fetch showtimes:", error);
      }
    };

    fetchEvents();
  }, []);

  const filteredEvents = events.filter(event =>
    selectedTheaters.has(event.theater)
  );

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6">This Week's Showtimes</h1>

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

      <Calendar
        localizer={localizer}
        events={filteredEvents}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 800 }}
        defaultView="week"
        views={['week']}
        step={60}
        timeslots={1}
        min={new Date(1970, 0, 1, 0, 0)}
        max={new Date(1970, 0, 1, 23, 59)}
        date={currentDate}
        onNavigate={(newDate) => setCurrentDate(newDate)}
        components={{
          event: EventComponent
        }}
        eventPropGetter={(event) => {
          const backgroundColor = event.theater === 'Musicbox' ? '#b91c1c' : '#1e3a8a';
          return {
            style: {
              backgroundColor,
              color: 'white',
              border: '2px solid rgba(255, 255, 255, 0.4)'
            }
          };
        }}
      />
    </div>
  );
}
