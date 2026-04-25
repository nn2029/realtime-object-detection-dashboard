import { Radio } from "lucide-react";
import { formatPercent } from "../lib/streamClient";
import type { StreamEvent } from "../types";

type Props = {
  events: StreamEvent[];
};

export function EventStream({ events }: Props) {
  return (
    <section className="event-panel" aria-label="detection event stream">
      <div className="section-heading">
        <h2>Event Stream</h2>
        <span>{events.length} events</span>
      </div>
      <div className="events">
        {events.length === 0 ? (
          <article className="event-row muted">
            <Radio size={16} />
            <div>
              <strong>Waiting for frames</strong>
              <span>--</span>
            </div>
          </article>
        ) : (
          events.map((event) => (
            <article className="event-row" key={event.id}>
              <Radio size={16} />
              <div>
                <strong>{event.summary}</strong>
                <span>
                  frame {event.frameId} / {formatPercent(event.confidence)} / {event.time}
                </span>
              </div>
              <b>{event.count}</b>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
