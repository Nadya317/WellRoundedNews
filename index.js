const express = require('express');
const cors = require('cors');
const pool = require('./db'); // Imports the database connection you just made

const app = express();

// Middleware
app.use(cors());
app.use(express.json()); // Allows your server to understand JSON data

// A simple test route to make sure the server works
app.get('/', (req, res) => {
    res.send("Hello from the News Aggregator Backend!");
});

// A test route to check the database connection
app.get('/test-db', async (req, res) => {
    try {
        const result = await pool.query('SELECT NOW()'); // A simple SQL query
        res.json(result.rows);
    } catch (err) {
        console.error(err.message);
        res.status(500).send("Database connection failed");
    }
});

// Start the server on port 5000
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});