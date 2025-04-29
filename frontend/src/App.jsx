import React, { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Home from './Home'
import { UpdateStock } from './components/UpdateStock';
import { StockInfo } from './components/StockInfo';

import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Register from './Register';
import Login from './Login';
import Search from './search'
import IntroPage from './Intropage'
// import Portfolio from './Portfolio';
// import StockData from './StocksData'
import Navbar from './components/Navbar'; 
import StockDisplay from './StockDisplay';
import StockData from './components/graph';
import StockGraph from './components/graph';


function App() {
  const [startDate, setStartDate] = useState('2010-01-01');
  const [endDate, setEndDate] = useState('2012-12-31');
  const [aggregate, setAggregate] = useState('monthly');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  return (
    <Router>
    <div>
      
      <Navbar isLoggedIn={isLoggedIn} onLogout={() => setIsLoggedIn(false)} />
      <Routes>
        <Route path="/" element={ <StockGraph startDate={startDate} endDate={endDate} aggregate={aggregate} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </div>
    </Router>
  );
}

export default App;


//     <StockData
//       startDate={startDate}
//       endDate={endDate}
//       aggregate={aggregate}
//     />
//   </div>
//     // <Router>
//     //   <div>
//     //     {/* Navbar always visible */}
//     //     <Navbar isLoggedIn={isLoggedIn} onLogout={handleLogout} />

//     //     {/* Define your routes here */}
//     //     <Routes>
//     //       <Route path="/" element={<IntroPage />} />
//     //       <Route path="/register" element={<Register />} />
//     //       <Route path="/login" element={<Login />} />
//     //       <Route path="/display" element={<StockDisplay />} />
//     //       {/* Add Portfolio, StockData, etc. routes later */}
//     //     </Routes>
//     //   </div>
//     // </Router>
//   );
// }

// export default App;
