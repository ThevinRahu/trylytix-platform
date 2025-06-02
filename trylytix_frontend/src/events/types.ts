// types.ts

// A rugby team
export interface Team {
  id: number;
  name: string;
  short_name?: string;
  logo_url?: string;
}

// A rugby player
export interface Player {
  id: number;
  name: string;
  position?: string;
  number?: number;
  team_id: number;
}

// Half type for match (1st half, 2nd half, etc.)
export type HalfType = '1H' | '2H' | 'ET';

// Rugby event structure
export interface RugbyEvent {
  id?: number; // Optional if not returned from backend
  match: number;
  player: number | null;
  team: number;
  event_type: string;
  is_opponent_event: boolean;
  minute: number;
  second: number;
  half: HalfType;
  x_coord: number;
  y_coord: number;
  location_zone: string;
  phase: number;
  description?: string;
  timestamp: string;
}
