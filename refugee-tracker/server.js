const express = require('express');
const app = express();
app.use(express.json());

// Demo data - represents sensitive refugee tracking data
const refugees = [
  { id: 'REF-001', status: 'safe', location: 'Camp Alpha', lastSeen: '2026-03-30', needs: ['medical', 'shelter'] },
  { id: 'REF-002', status: 'transit', location: 'Border Crossing B', lastSeen: '2026-03-31', needs: ['food', 'documents'] },
  { id: 'REF-003', status: 'missing', location: 'Unknown', lastSeen: '2026-03-28', needs: ['urgent-search'] },
  { id: 'REF-004', status: 'safe', location: 'Camp Beta', lastSeen: '2026-03-31', needs: ['education'] },
  { id: 'REF-005', status: 'critical', location: 'Medical Facility C', lastSeen: '2026-03-31', needs: ['medical', 'family-reunification'] },
];

const alerts = [];

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'refugee-tracker' });
});

// Get all refugees (summary only - no PII)
app.get('/refugees', (req, res) => {
  const summary = refugees.map(r => ({
    id: r.id,
    status: r.status,
    lastSeen: r.lastSeen,
    needsCount: r.needs.length
  }));
  res.json({ total: refugees.length, data: summary });
});

// Get refugee by ID
app.get('/refugees/:id', (req, res) => {
  const refugee = refugees.find(r => r.id === req.params.id);
  if (!refugee) return res.status(404).json({ error: 'Not found' });
  res.json(refugee);
});

// Get status summary
app.get('/status', (req, res) => {
  const summary = refugees.reduce((acc, r) => {
    acc[r.status] = (acc[r.status] || 0) + 1;
    return acc;
  }, {});
  res.json({
    summary,
    critical: refugees.filter(r => r.status === 'critical' || r.status === 'missing').length,
    total: refugees.length,
    lastUpdated: new Date().toISOString()
  });
});

// Create alert
app.post('/alerts', (req, res) => {
  const alert = {
    id: `ALT-${Date.now()}`,
    ...req.body,
    timestamp: new Date().toISOString()
  };
  alerts.push(alert);
  res.status(201).json(alert);
});

// Get alerts
app.get('/alerts', (req, res) => {
  res.json({ total: alerts.length, data: alerts });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Refugee Tracker API running on port ${PORT}`);
});
