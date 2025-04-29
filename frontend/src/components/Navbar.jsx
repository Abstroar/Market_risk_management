import { useState } from 'react';
import { Link } from 'react-router-dom'; // React Router for page navigation
import './navbar.css'; // Import your navbar styles here
import { searchStock } from '../api/search';
import { useNavigate } from 'react-router-dom';

function Navbar({ isLoggedIn, onLogout }) {
  const navigate = useNavigate();
  const [searchSymbol, setSearchSymbol] = useState('');
  
  const handleSearchChange = (e) => {
    setSearchSymbol(e.target.value);
  };
  
  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    try {
      const stockData = await searchStock(searchSymbol);
      console.log('Stock Data:', stockData);
      
      // Navigate to display page and pass stock data
      navigate('/display', { state: { stockData } });
    } catch (error) {
      console.error('Error fetching stock:', error);
      alert('Stock not found!');
    }
  };
  
  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo / Home Link */}
        <Link to="/" className="navbar-logo">
          StockTracker
        </Link>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="navbar-search">
          <input 
            type="text" 
            placeholder="Search Stock..." 
            value={searchSymbol} 
            onChange={handleSearchChange} 
          />
          <button type="submit">Search</button>
        </form>

        {/* Right Side - Links */}
        <div className="navbar-links">
          {!isLoggedIn ? (
            <>
              <Link to="/login" className="navbar-link">Login</Link>
              <Link to="/register" className="navbar-link">Sign Up</Link>
            </>
          ) : (
            <>
              <Link to="/portfolio" className="navbar-link">Portfolio</Link>
              <button onClick={onLogout} className="navbar-link">Logout</button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
