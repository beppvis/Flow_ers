// Mock Fleetbase server implementation

const express = require('express');
// const { Pool } = require('pg'); // Removed for mock
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// In-memory store for our mock
const db = {
    drivers: [],
    orders: [],
    assignments: []
};

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', service: 'fleetbase-mock' });
});

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'Fleetbase API Mock',
        version: '1.0.0',
        status: 'running',
        counts: {
            drivers: db.drivers.length,
            orders: db.orders.length
        }
    });
});

// --- Drivers API ---
app.post('/drivers', (req, res) => {
    const driver = {
        id: `dr_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
        name: req.body.name || 'Unknown Driver',
        status: req.body.status || 'active',
        created_at: new Date().toISOString()
    };
    db.drivers.push(driver);
    console.log(`[Fleetbase] Created driver: ${driver.name} (${driver.id})`);
    res.status(201).json(driver);
});

app.get('/drivers', (req, res) => {
    res.json(db.drivers);
});

// --- Orders API ---
app.post('/orders', (req, res) => {
    const order = {
        id: `ord_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
        payload: req.body,
        status: 'created',
        created_at: new Date().toISOString()
    };
    db.orders.push(order);
    console.log(`[Fleetbase] Created order: ${order.id}`);
    res.status(201).json(order);
});

app.get('/orders', (req, res) => {
    res.json(db.orders);
});

// --- Assignment/Dispatch API ---
app.post('/orders/:id/dispatch', (req, res) => {
    const { id } = req.params;
    const { driver_id } = req.body;

    const order = db.orders.find(o => o.id === id);
    if (!order) {
        return res.status(404).json({ error: 'Order not found' });
    }

    const driver = db.drivers.find(d => d.id === driver_id);
    // Optional: Checking if driver exists, but let's be loose for mock

    order.status = 'dispatched';
    order.driver_id = driver_id;

    console.log(`[Fleetbase] Dispatched order ${id} to driver ${driver_id}`);

    res.json({
        success: true,
        order: order
    });
});

// Start server
app.listen(port, () => {
    console.log(`Fleetbase Mock API server running on port ${port}`);
});


