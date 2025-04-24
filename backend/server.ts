import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect('mongodb://localhost:27017/login-app')
  .then(() => console.log('Connected to MongoDB'))
  .catch((err) => console.error('MongoDB connection error:', err));

// Simple user schema
const userSchema = new mongoose.Schema({
  email: String,
  password: String
});

const User = mongoose.model('User', userSchema);

// Register route
app.post('/api/register', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Create new user
    const user = new User({ email, password });
    await user.save();
    
    res.json({ message: 'User created' });
  } catch (error) {
    res.status(500).json({ message: 'Error' });
  }
});

// Login route
app.post('/api/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user in database
    const user = await User.findOne({ email, password });
    
    if (user) {
      res.json({ message: 'Login successful' });
    } else {
      res.status(401).json({ message: 'Invalid credentials' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Error' });
  }
});

app.listen(5000, () => {
  console.log('Server running on port 5000');
}); 