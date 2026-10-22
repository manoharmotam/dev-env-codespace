const express = require('express');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

const POSTGRES_URI = process.env.POSTGRES_URI || 'postgresql://postgres:postgres@localhost:5432/tiffinstore';
const pool = new Pool({ connectionString: POSTGRES_URI });

// Initialize table and seed default user
async function initDB() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        default_address TEXT
      );
    `);
    await pool.query(`
      INSERT INTO users (user_id, name, email, default_address)
      VALUES ('user-101', 'Ravi Kumar', 'ravi@tiffinstore.com', 'Plot 42, MG Road, Secunderabad')
      ON CONFLICT (user_id) DO NOTHING;
    `);
    console.log('User DB initialized in PostgreSQL');
  } catch (err) {
    console.error('Database initialization error (will retry on requests):', err.message);
  }
}
initDB();

app.get('/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'healthy', service: 'user-service', db: 'PostgreSQL' });
  } catch (e) {
    res.status(500).json({ status: 'unhealthy', error: e.message });
  }
});

app.get('/api/users/:userId', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM users WHERE user_id = $1', [req.params.userId]);
    if (result.rows.length === 0) return res.status(404).json({ error: 'User not found' });
    res.json(result.rows[0]);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.listen(5002, () => console.log('User service listening on port 5002'));