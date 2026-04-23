const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

const INITIAL_TIMER = 20;   // seconds for first bid window
const BID_BONUS     = 10;   // seconds added on each bid
const NEXT_IN_START = 10;   // countdown before next player

// ── State ──────────────────────────────────────────────────────────────────
let state = {
  phase: 'setup',   // setup | ready | bidding | sold | unsold | paused | countdown | finished
  owners: [],
  players: [],
  currentIndex: -1,
  currentPlayer: null,
  currentBid: 0,
  leaderId: null,
  leaderName: null,
  timer: INITIAL_TIMER,
  nextIn: 0,
  bidLog: [],
  soldLog: [],
  totalPlayers: 0,
};

let timerInterval  = null;
let nextInInterval = null;

// ── Broadcast ──────────────────────────────────────────────────────────────
function broadcast() { io.emit('state', publicState()); }

function publicState() {
  return {
    phase: state.phase,
    owners: state.owners.map(o => ({
      id: o.id, name: o.name, budget: o.budget,
      squad: o.squad, connected: o.connected,
    })),
    currentIndex:  state.currentIndex,
    currentPlayer: state.currentPlayer,
    currentBid:    state.currentBid,
    leaderId:      state.leaderId,
    leaderName:    state.leaderName,
    timer:         state.timer,
    nextIn:        state.nextIn,
    bidLog:        state.bidLog,
    soldLog:       state.soldLog,
    totalPlayers:  state.totalPlayers,
  };
}

// ── Timer ──────────────────────────────────────────────────────────────────
function startTimer(seconds) {
  clearInterval(timerInterval);
  state.timer = seconds;
  broadcast();

  timerInterval = setInterval(() => {
    if (state.phase !== 'bidding') { clearInterval(timerInterval); return; }
    state.timer--;
    broadcast();

    if (state.timer <= 0) {
      clearInterval(timerInterval);
      state.leaderId ? doSell() : doUnsold();
    }
  }, 1000);
}

// ── Next-player countdown ──────────────────────────────────────────────────
function startNextInCountdown() {
  clearInterval(nextInInterval);
  state.phase  = state.phase; // keep sold/unsold for display
  state.nextIn = NEXT_IN_START;
  broadcast();

  nextInInterval = setInterval(() => {
    state.nextIn--;
    broadcast();
    if (state.nextIn <= 0) {
      clearInterval(nextInInterval);
      advancePlayer();
    }
  }, 1000);
}

// ── Sell / Unsold ──────────────────────────────────────────────────────────
function doSell() {
  const owner = state.owners.find(o => o.id === state.leaderId);
  if (!owner) return;

  owner.budget -= state.currentBid;
  owner.squad.push({ ...state.currentPlayer, soldPrice: state.currentBid });
  state.soldLog.push({
    player:    state.currentPlayer,
    ownerName: owner.name,
    ownerId:   owner.id,
    amount:    state.currentBid,
  });

  state.phase = 'sold';
  broadcast();
  startNextInCountdown();
}

function doUnsold() {
  state.phase = 'unsold';
  broadcast();
  startNextInCountdown();
}

function advancePlayer() {
  clearInterval(timerInterval);
  clearInterval(nextInInterval);

  const next = state.currentIndex + 1;
  if (next >= state.players.length) {
    state.phase = 'finished';
    state.currentPlayer = null;
    broadcast();
    return;
  }

  state.currentIndex  = next;
  state.currentPlayer = state.players[next];
  state.currentBid    = 0;
  state.leaderId      = null;
  state.leaderName    = null;
  state.bidLog        = [];
  state.nextIn        = 0;
  state.phase         = 'bidding';
  startTimer(INITIAL_TIMER);
}

// ── Socket Events ──────────────────────────────────────────────────────────
io.on('connection', (socket) => {
  socket.emit('state', publicState());

  socket.on('owner:join', ({ ownerId }) => {
    const owner = state.owners.find(o => o.id === ownerId);
    if (owner) { owner.connected = true; owner.socketId = socket.id; broadcast(); }
  });

  socket.on('disconnect', () => {
    const owner = state.owners.find(o => o.socketId === socket.id);
    if (owner) { owner.connected = false; broadcast(); }
  });

  // Admin
  socket.on('admin:setOwners', (names) => {
    state.owners = names.map((name, i) => ({
      id: `owner_${i + 1}`, name,
      budget: 100, squad: [],
      connected: false, socketId: null,
    }));
    if (state.players.length > 0) state.phase = 'ready';
    broadcast();
  });

  socket.on('admin:loadPlayers', (players) => {
    state.players      = players;
    state.totalPlayers = players.length;
    state.currentIndex = -1;
    state.currentPlayer = null;
    state.phase = state.owners.length > 0 ? 'ready' : 'setup';
    broadcast();
  });

  socket.on('admin:start', () => {
    if (!['ready'].includes(state.phase)) return;
    advancePlayer();
  });

  socket.on('admin:next', () => {
    clearInterval(timerInterval);
    clearInterval(nextInInterval);
    advancePlayer();
  });

  socket.on('admin:skip', () => {
    clearInterval(timerInterval);
    clearInterval(nextInInterval);
    const skipped = state.players.splice(state.currentIndex, 1)[0];
    state.players.push(skipped);
    state.currentIndex--;
    advancePlayer();
  });

  socket.on('admin:pause', () => {
    if (state.phase !== 'bidding') return;
    clearInterval(timerInterval);
    state.phase = 'paused';
    broadcast();
  });

  socket.on('admin:resume', () => {
    if (state.phase !== 'paused') return;
    state.phase = 'bidding';
    startTimer(state.timer);
  });

  socket.on('admin:reset', () => {
    clearInterval(timerInterval);
    clearInterval(nextInInterval);
    state = {
      phase: 'setup', owners: [], players: [],
      currentIndex: -1, currentPlayer: null,
      currentBid: 0, leaderId: null, leaderName: null,
      timer: INITIAL_TIMER, nextIn: 0,
      bidLog: [], soldLog: [], totalPlayers: 0,
    };
    broadcast();
  });

  // Owner bid — adds BID_BONUS seconds to current timer
  socket.on('owner:bid', ({ ownerId, amount }) => {
    if (state.phase !== 'bidding') return;

    const owner = state.owners.find(o => o.id === ownerId);
    if (!owner) return;

    const amt  = parseInt(amount);
    if (isNaN(amt) || amt < 1)         return;
    if (amt <= state.currentBid)        return;
    if (amt > owner.budget)             return;

    const base = parseInt(state.currentPlayer?.base_price) || 1;
    if (state.currentBid === 0 && amt < base) return;

    state.currentBid  = amt;
    state.leaderId    = owner.id;
    state.leaderName  = owner.name;

    state.bidLog.unshift({ ownerName: owner.name, ownerId: owner.id, amount: amt });
    if (state.bidLog.length > 8) state.bidLog.pop();

    // Add bonus time to current timer
    startTimer(state.timer + BID_BONUS);

    io.emit('bid:flash', { ownerName: owner.name, amount: amt });
    broadcast();
  });
});

// Owner page route
app.get('/owner/:id', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'owner.html'));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`\n⚡ MPL E-Bidding running at http://localhost:${PORT}`);
  console.log(`   Display : http://localhost:${PORT}/display.html`);
  console.log(`   Admin   : http://localhost:${PORT}/admin.html`);
  console.log(`   Owner   : http://localhost:${PORT}/owner/owner_1\n`);
});
