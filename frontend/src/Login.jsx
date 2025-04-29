import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Login.css"
function Login() {
  const [formData, setFormData] = useState({
    username: "",
    password: ""
  });

  const navigate = useNavigate(); // useNavigate hook for routing after success

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://127.0.0.1:8000/login", formData);
      alert("Logged in successfully!");
      navigate("/portfolio");  // Redirect to Portfolio page after login
    } catch (error) {
      alert(error.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="login-container">
  <h2>Login</h2>
  <form onSubmit={handleSubmit}>
      <input name="username" placeholder="Username" onChange={handleChange} /><br />
      <input name="password" type="password" placeholder="Password" onChange={handleChange} /><br />
      <button type="submit">Login</button>
    </form>
  </div>
  );
}

export default Login;
