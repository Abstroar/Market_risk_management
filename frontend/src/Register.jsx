import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import '/Register.css'


function Register() {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    age: "",
    gender: "",
    profile_img: ""
  });

  const navigate = useNavigate(); // useNavigate hook for routing after success

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://127.0.0.1:8000/register", formData);
      alert("Registered successfully!");
      navigate("/login");  // Redirect to Login page after successful registration
    } catch (error) {
      alert(error.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="register-container">
  <h2>Register</h2>
  <form onSubmit={handleSubmit}>
    <input name="username" placeholder="Username" onChange={handleChange} /><br />
    <input name="password" type="password" placeholder="Password" onChange={handleChange} /><br />
    <input name="age" type="number" placeholder="Age" onChange={handleChange} /><br />
    <input name="gender" placeholder="Gender" onChange={handleChange} /><br />
    <input name="profile_img" placeholder="Profile Image URL" onChange={handleChange} /><br />
    <button type="submit">Register</button>
  </form>
</div>
  );
}

export default Register;
