import express from 'express';
const app = express();

app.get('/test', (req, res) => {
  res.json({ message: 'Simple test server working', port: 5000 });
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Simple test server running on port 5000');
});