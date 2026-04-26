const { Pool } = require('pg');

// Replace these values with your actual PostgreSQL setup from Phase 02
const pool = new Pool({
  user: 'postgres',         // Your postgres username
  password: '24kMagic!', // Your postgres password
  host: 'localhost',        // Usually localhost
  port: 5432,               // Default postgres port
  database: 'WellRoundedNews' // The name of the DB you made in Phase 1/2
});

module.exports = pool;