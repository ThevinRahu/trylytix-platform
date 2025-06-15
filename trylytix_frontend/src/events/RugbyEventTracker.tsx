import React, { useState, useEffect } from "react";
import {
  AppBar, Toolbar, Typography, Button, Paper, Box, Dialog, DialogTitle, DialogContent, DialogActions,
  Snackbar, Alert, Stack, TextField,
  ToggleButtonGroup,
  ToggleButton
} from "@mui/material";
import { PlayArrow, Pause, Replay, SportsRugby, UploadFile } from "@mui/icons-material";
import Papa from "papaparse";
import axios from "axios";

// --- Types
type Player = { id: number; full_name: string; jersey_number: number; team: number };
type RugbyEvent = {
  id?: number;
  match: number;
  player: number;
  player_name?: string;
  team: number;
  event_type: string;
  is_opponent_event: boolean;
  minute: number;
  second: number;
  half: string;
  x_coord: number;
  y_coord: number;
  location_zone: string;
  phase: number;
  description: string;
  timestamp: string;
};
type HalfType = "1H" | "2H" | "ET";

const EVENT_TYPES = [
  "advantage","box_kick","carry","conversion","conversion_missed","defensive_line_break","drop_goal","forward_pass","free_kick","foul_play","grubber_kick","high_tackle","holding_on","in_touch","injury","interception","kick","kick_return","kickoff","knock_on","line_break","lineout","lineout_loss","lineout_win","maul","missed_tackle","not_releasing","offload","offside","pass","penalty","penalty_goal","penalty_missed","referee_call","restart","restart_22","ruck","run","scrum","scrum_loss","scrum_win","sin_bin","substitution","tackle","timeout","try","try_assist","turnover","yellow_card","red_card"
];

const homeTeamId = 4;
const awayTeamId = 5;
const MATCH_ID = 1; // Change if needed

const RugbyEventTracker: React.FC = () => {
  // State
  const [homePlayers, setHomePlayers] = useState<Player[]>([]);
  const [awayPlayers, setAwayPlayers] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [selectedCoords, setSelectedCoords] = useState<{ x: number; y: number; zone: string } | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [description, setDescription] = useState<string>("");
  const [phase, setPhase] = useState<number>(1);
  const [half, setHalf] = useState<HalfType>("1H");
  const [matchTime, setMatchTime] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [events, setEvents] = useState<RugbyEvent[]>([]);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" | "info" }>({ open: false, message: "", severity: "info" });
  const [uploading, setUploading] = useState<boolean>(false);
  const [confirmDialog, setConfirmDialog] = useState<boolean>(false);

  // Timer logic
  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => {
      setMatchTime(prev => {
        if (prev >= 2700 && half === "1H") {
          setHalf("2H");
        }
        return prev + 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isRunning, half]);

  // Fetch teams and players (only teams 4 and 5)
  useEffect(() => {
    // Replace with your API logic, for now just fetch teams 4 and 5 and their players
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ4OTM4NDg4LCJpYXQiOjE3NDg4NTIwODgsImp0aSI6ImU1ZjMzZGQzNWExOTQzMzE4MjFkZmJkZjhjMWRmMjZhIiwidXNlcl9pZCI6MX0.Dia5xKbJUEycsdGWo1elHTSd4mNFZiP3AXmv0YBYCLo"; // Assuming you store JWT in localStorage
    const fetchTeamsAndPlayers = async () => {
      try {
        // hardcoded for now, replace with API calls as needed
        // const teamsResp = await axios.get<Team[]>("http://127.0.0.1:8000/api/teams/4/", {
        //    headers: {
        //     Authorization: `Bearer ${token}`,
        //   },
        // });
        // setTeams(teamsResp.data);
        const players = await axios.get<Player[]>("http://127.0.0.1:8000/api/players/", {
           headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const playersResp = players.data.filter((p) => p.team === 4 || p.team === 5);
        // --- UI
        const homePlayers = playersResp.filter(p => p.team === homeTeamId).sort((a, b) => a.jersey_number - b.jersey_number);
        const awayPlayers = playersResp.filter(p => p.team === awayTeamId).sort((a, b) => a.jersey_number - b.jersey_number);
        setHomePlayers(homePlayers);
        setAwayPlayers(awayPlayers);
      } catch (err) {
        setSnackbar({ open: true, message: "Error fetching teams/players", severity: "error" });
      }
    };
    fetchTeamsAndPlayers();
  }, []);

  // --- Handlers
  const handleFieldClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    let zone = "Midfield";
    if (x < 22) zone = "Own 22";
    else if (x < 50) zone = "Own Half";
    else if (x < 78) zone = "Opponent Half";
    else zone = "Opponent 22";
    setSelectedCoords({ x: Number(x.toFixed(2)), y: Number(y.toFixed(2)), zone });
    setSelectedEvent(null); // reset event selection
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  const handleRecordEvent = () => {
    if (!selectedPlayer || !selectedCoords || !selectedEvent) {
      setSnackbar({ open: true, message: "Select player, field, and event", severity: "error" });
      return;
    }
    const newEvent: RugbyEvent = {
      match: MATCH_ID,
      player: selectedPlayer.id,
      player_name: selectedPlayer.full_name,
      team: selectedPlayer.team,
      event_type: selectedEvent,
      is_opponent_event: selectedPlayer.team === awayTeamId, // you can change logic if needed
      minute: Math.floor(matchTime / 60),
      second: matchTime % 60,
      half,
      x_coord: selectedCoords.x,
      y_coord: selectedCoords.y,
      location_zone: selectedCoords.zone,
      phase,
      description,
      timestamp: new Date().toISOString(),
    };
    setEvents(prev => [...prev, newEvent]);
    setSelectedEvent(null);
    setDescription("");
    setSelectedCoords(null);
    setPhase(ph => ph + 1);
    setSnackbar({ open: true, message: "Event recorded!", severity: "success" });
    // keep selectedPlayer for speed
  };

  // --- Upload CSV
  const uploadCSV = async () => {
    setUploading(true);
    try {
      const csv = Papa.unparse(events.map(ev => ({
        event_type: ev.event_type,
        timestamp: ev.timestamp,
        x: ev.x_coord,
        y: ev.y_coord,
        zone: ev.location_zone,
        description: ev.description,
        player_id: ev.player,
        team_id: ev.team,
        phase: ev.phase,
        is_opponent_event: ev.is_opponent_event
      })));
      const blob = new Blob([csv], { type: "text/csv" });
      const formData = new FormData();
      formData.append("file", blob, "events.csv");
      formData.append("match_id", String(MATCH_ID));
      await axios.post("http://127.0.0.1:8000/api/events/upload-csv/", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setSnackbar({ open: true, message: "CSV uploaded successfully!", severity: "success" });
      setEvents([]);
    } catch (err) {
      setSnackbar({ open: true, message: "CSV upload failed. Check your connection.", severity: "error" });
    } finally {
      setUploading(false);
      setConfirmDialog(false);
    }
  };

  

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <SportsRugby sx={{ mr: 2 }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Rugby Match Event Tracker</Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Typography variant="h6">{half} {formatTime(matchTime)}</Typography>
            <ToggleButtonGroup exclusive>
              <ToggleButton value="play" selected={isRunning} onClick={() => setIsRunning(true)}>
                <PlayArrow />
              </ToggleButton>
              <ToggleButton value="pause" selected={!isRunning} onClick={() => setIsRunning(false)}>
                <Pause />
              </ToggleButton>
              <ToggleButton value="reset" onClick={() => { setMatchTime(0); setHalf("1H"); }}>
                <Replay />
              </ToggleButton>
            </ToggleButtonGroup>
            <Button
              variant="outlined"
              size="small"
              onClick={() => setHalf(half === "1H" ? "2H" : "1H")}
            >
              {half === "1H" ? "Switch to 2H" : "Switch to 1H"}
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Box sx={{ p: 2 }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="flex-start">
          {/* Home Players */}
          <Stack spacing={1} alignItems="flex-end" sx={{ minWidth: 150, width: { xs: "100%", md: 150 } }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>Home</Typography>
            {homePlayers.map(p => (
              <Button
                key={p.id}
                variant={selectedPlayer?.id === p.id ? "contained" : "outlined"}
                color="primary"
                fullWidth
                onClick={() => setSelectedPlayer(p)}
              >
                #{p.jersey_number} {p.full_name}
              </Button>
            ))}
          </Stack>

          {/* Field */}
          <Box sx={{ flex: 1, mx: 2, minWidth: 330 }}>
            <Paper
              elevation={3}
              sx={{ height: 420, position: "relative", backgroundColor: "success.main", border: "2px solid #ccc", cursor: "crosshair" }}
              onClick={handleFieldClick}
            >
              {/* Marker */}
              {selectedCoords &&
                <Box sx={{
                  position: "absolute", width: 20, height: 20, borderRadius: "50%", bgcolor: "primary.main",
                  left: `${selectedCoords.x}%`, top: `${selectedCoords.y}%`, transform: "translate(-50%, -50%)"
                }} />
              }
              {/* Home/Away Labels */}
              <Typography sx={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "#fff" }}>Home</Typography>
              <Typography sx={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", color: "#fff" }}>Away</Typography>
            </Paper>
            {/* Show zone label */}
            {selectedCoords && <Typography align="center" sx={{ mt: 1 }}>Zone: {selectedCoords.zone}</Typography>}
          </Box>

          {/* Away Players */}
          <Stack spacing={1} alignItems="flex-start" sx={{ minWidth: 150, width: { xs: "100%", md: 150 } }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>Away</Typography>
            {awayPlayers.map(p => (
              <Button
                key={p.id}
                variant={selectedPlayer?.id === p.id ? "contained" : "outlined"}
                color="secondary"
                fullWidth
                onClick={() => setSelectedPlayer(p)}
              >
                #{p.jersey_number} {p.full_name}
              </Button>
            ))}
          </Stack>
        </Stack>

        {/* Event Selection */}
        {selectedPlayer && selectedCoords &&
          <Paper sx={{ my: 2, p: 2 }}>
            <Typography>Select Event:</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {EVENT_TYPES.map(evt => (
                <Button
                  key={evt}
                  variant={selectedEvent === evt ? "contained" : "outlined"}
                  onClick={() => setSelectedEvent(evt)}
                  size="small"
                  sx={{ m: 0.5, minWidth: 100 }}
                >
                  {evt.replace("_", " ")}
                </Button>
              ))}
            </Stack>
            {/* Description & Confirm */}
            {selectedEvent &&
              <>
                <TextField
                  fullWidth
                  label="Description (optional)"
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  sx={{ my: 2 }}
                />
                <Button
                  variant="contained"
                  color="success"
                  onClick={handleRecordEvent}
                  sx={{ width: "100%", py: 2 }}
                  size="large"
                >Done / Record Event</Button>
              </>
            }
          </Paper>
        }

        {/* Recent events, CSV upload */}
        <Box mt={3}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <Typography variant="h6">Match Events ({events.length})</Typography>
              <Button
                variant="contained"
                color="success"
                startIcon={<UploadFile />}
                disabled={events.length === 0 || uploading}
                onClick={() => setConfirmDialog(true)}
              >
                Upload CSV
              </Button>
            </Box>
            <Box sx={{ maxHeight: 340, overflow: "auto" }}>
              {events.slice().reverse().map((event, idx) => (
                <Box key={event.timestamp + idx} sx={{ borderBottom: "1px solid #eee", py: 1 }}>
                  <Typography variant="body2">
                    [{event.half} {formatTime(event.minute * 60 + event.second)}] {event.event_type.replace("_", " ")} — {event.player_name || "Unknown"} ({event.location_zone})
                  </Typography>
                  {event.description && <Typography variant="caption">{event.description}</Typography>}
                </Box>
              ))}
              {events.length === 0 && (
                <Typography variant="body2">No events recorded yet</Typography>
              )}
            </Box>
          </Paper>
        </Box>
      </Box>

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: "100%" }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Confirm dialog for upload */}
      <Dialog open={confirmDialog} onClose={() => setConfirmDialog(false)}>
        <DialogTitle>Upload Events as CSV</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to upload all {events.length} events to the server? This cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog(false)}>Cancel</Button>
          <Button
            onClick={uploadCSV}
            color="success"
            variant="contained"
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RugbyEventTracker;