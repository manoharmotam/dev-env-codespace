const express = require('express');
const { createClient } = require('redis');

const app = express();
app.use(express.json());

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const redisClient = createClient({ url: REDIS_URL });
redisClient.connect().catch(console.error);

app.get('/health', async (req, res) => {
  const isReady = redisClient.isReady;
  res.status(isReady ? 200 : 500).json({ status: isReady ? 'healthy' : 'unhealthy', service: 'cart-service', db: 'Redis' });
});

app.get('/api/cart/:userId', async (req, res) => {
  const data = await redisClient.get(`cart:${req.params.userId}`);
  res.json({ userId: req.params.userId, items: data ? JSON.parse(data) : [] });
});

app.post('/api/cart/:userId', async (req, res) => {
  const { item_id, name, price, qty } = req.body;
  const key = `cart:${req.params.userId}`;
  let current = await redisClient.get(key);
  let items = current ? JSON.parse(current) : [];
  items.push({ item_id, name, price, qty });
  // Expire cart after 1 hour (3600 seconds)
  await redisClient.setEx(key, 3600, JSON.stringify(items));
  res.json({ message: 'Added to tiffin box!', items });
});

app.listen(5003, () => console.log('Cart service listening on port 5003'));