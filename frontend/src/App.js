import React, { useState, useEffect } from 'react';
import './index.css';

// Logo component with animation
const Logo = () => (
  <div className="logo" style={{ fontSize: '3rem', fontWeight: 'bold', color: 'var(--primary)' }}>
    <span style={{ color: 'var(--primary)' }}>Learn</span>
    <span style={{ color: 'var(--secondary)' }}>Aid</span>
  </div>
);

// Animated card component
const Card = ({ title, icon, description, color, delay, onClick }) => {
  return (
    <div 
      className="card"
      onClick={onClick}
      style={{ 
        backgroundColor: 'var(--white)',
        borderRadius: '12px',
        padding: '25px',
        margin: '15px',
        boxShadow: '0 5px 15px rgba(0,0,0,0.1)',
        cursor: 'pointer',
        animationDelay: `${delay}s`,
        border: `2px solid var(--${color})`,
        transition: 'transform 0.3s ease, box-shadow 0.3s ease'
      }}
    >
      <div style={{ 
        backgroundColor: `var(--${color})`, 
        borderRadius: '50%', 
        width: '60px', 
        height: '60px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        marginBottom: '15px' 
      }}>
        <span style={{ fontSize: '30px', color: 'white' }}>{icon}</span>
      </div>
      <h3 style={{ color: `var(--${color})`, marginBottom: '10px' }}>{title}</h3>
      <p style={{ color: 'var(--dark)', opacity: 0.8 }}>{description}</p>
    </div>
  );
};

// Button component with animation
const Button = ({ text, color, onClick }) => {
  return (
    <button 
      className="btn ripple"
      onClick={onClick}
      style={{ 
        backgroundColor: `var(--${color})`,
        color: 'white',
        border: 'none',
        borderRadius: '30px',
        padding: '12px 25px',
        fontSize: '16px',
        fontWeight: 'bold',
        cursor: 'pointer',
        margin: '10px'
      }}
    >
      {text}
    </button>
  );
};

// Modal component for login
const LoginModal = ({ role, onClose }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Credentials based on role
  let defaultCredentials = {
    username: "user@example.com",
    password: "password123"
  };

  if (role === 'Admin') {
    defaultCredentials = {
      username: "admin@learnaid.edu",
      password: "admin123"
    };
  } else if (role === 'Faculty') {
    defaultCredentials = {
      username: "john.doe@learnaid.edu",
      password: "faculty123"
    };
  } else if (role === 'Student') {
    defaultCredentials = {
      username: "alice.johnson@student.learnaid.edu",
      password: "student123"
    };
  }

  useEffect(() => {
    // Autofill credentials
    setUsername(defaultCredentials.username);
    setPassword(defaultCredentials.password);
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      // Redirect to API docs for now
      window.location.href = 'http://localhost:8000/docs';
    }, 1500);
  };

  const getRoleColor = () => {
    if (role === 'Admin') return 'primary';
    if (role === 'Faculty') return 'secondary';
    return 'success';
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000,
      animation: 'fadeIn 0.3s ease-out'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '30px',
        width: '400px',
        maxWidth: '90%',
        animation: 'slideUp 0.4s ease-out',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ color: `var(--${getRoleColor()})`, margin: 0 }}>{role} Login</h2>
          <button 
            onClick={onClose} 
            style={{ 
              backgroundColor: 'transparent', 
              border: 'none', 
              fontSize: '20px',
              cursor: 'pointer',
              color: 'var(--dark)'
            }}
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Username</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '10px', 
                borderRadius: '6px', 
                border: '1px solid #ddd',
                fontSize: '16px'
              }}
              placeholder="Enter username"
            />
          </div>

          <div style={{ marginBottom: '30px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '10px', 
                borderRadius: '6px', 
                border: '1px solid #ddd',
                fontSize: '16px'
              }}
              placeholder="Enter password"
            />
          </div>

          <Button 
            text={isLoading ? "Logging in..." : "Login"} 
            color={getRoleColor()} 
            onClick={handleLogin}
          />
        </form>

        <div style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '15px' }}>
          <p style={{ fontSize: '14px', color: 'var(--dark)', opacity: 0.7 }}>
            Default Credentials: <br/>
            Username: {defaultCredentials.username} <br/>
            Password: {defaultCredentials.password}
          </p>
        </div>
      </div>
    </div>
  );
};

// Main App component
function App() {
  const [selectedRole, setSelectedRole] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Add loading animation
    setTimeout(() => {
      setIsLoaded(true);
    }, 300);
  }, []);

  const handleRoleClick = (role) => {
    setSelectedRole(role);
    setShowModal(true);
  };

  return (
    <div className="page-transition" style={{ 
      opacity: isLoaded ? 1 : 0,
      transition: 'opacity 0.5s ease-in-out',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%)'
    }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%)',
        padding: '20px 0',
        color: 'white',
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        <div className="logo" style={{ animation: 'float 3s infinite ease-in-out' }}>
          <Logo />
        </div>
        <h1 style={{ marginTop: '10px', fontWeight: '600' }} className="text-animate">
          Intelligent Learning & Performance Support System
        </h1>
      </header>

      {/* Main content */}
      <main style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '40px 20px',
        textAlign: 'center'
      }}>
        <h2 className="text-animate" style={{ 
          marginBottom: '40px',
          color: 'var(--dark)',
          fontWeight: '600',
          animation: 'slideUp 0.8s ease-out'
        }}>
          Welcome to LearnAid! Select Your Role
        </h2>

        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          justifyContent: 'center',
          margin: '0 -15px'
        }}>
          <Card 
            title="Admin" 
            icon="👑" 
            description="Manage faculty, students, departments and view high-level analytics."
            color="primary"
            delay={0.1}
            onClick={() => handleRoleClick('Admin')}
          />
          
          <Card 
            title="Faculty" 
            description="Manage courses, create exams, assign tasks and track student performance."
            color="secondary"
            icon="👨‍🏫"
            delay={0.3}
            onClick={() => handleRoleClick('Faculty')}
          />
          
          <Card 
            title="Student" 
            description="View assigned courses, complete tasks and interact with the learning chatbot."
            color="success"
            icon="👨‍🎓"
            delay={0.5}
            onClick={() => handleRoleClick('Student')}
          />
        </div>

        <div style={{ marginTop: '60px', animation: 'fadeIn 1s ease-out' }}>
          <h3>System Features</h3>
          <div style={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            justifyContent: 'center', 
            gap: '20px',
            margin: '30px 0' 
          }}>
            <FeatureBadge icon="📊" text="Analytics Dashboard" />
            <FeatureBadge icon="🤖" text="AI Chatbot" />
            <FeatureBadge icon="📝" text="Auto-Generated Tasks" />
            <FeatureBadge icon="📚" text="Course Management" />
            <FeatureBadge icon="🧠" text="Performance Tracking" />
          </div>
        </div>

        <div style={{ marginTop: '40px', animation: 'slideUp 1.2s ease-out' }}>
          <Button 
            text="API Documentation" 
            color="info" 
            onClick={() => window.open('http://localhost:8000/docs', '_blank')}
          />
          <Button 
            text="Project Details" 
            color="dark" 
            onClick={() => window.open('https://github.com/ST-SARAVANAPRIYAN/LearnAid', '_blank')}
          />
        </div>
      </main>

      {/* Footer */}
      <footer style={{
        backgroundColor: 'var(--dark)',
        color: 'white',
        padding: '20px',
        textAlign: 'center',
        marginTop: '40px'
      }}>
        <p>© 2025 LearnAid | Intelligent Learning & Performance Support System</p>
      </footer>

      {/* Login Modal */}
      {showModal && (
        <LoginModal 
          role={selectedRole} 
          onClose={() => setShowModal(false)} 
        />
      )}
    </div>
  );
}

// Feature badge component
const FeatureBadge = ({ icon, text }) => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    backgroundColor: 'var(--white)',
    borderRadius: '30px',
    padding: '10px 20px',
    boxShadow: '0 3px 10px rgba(0,0,0,0.1)',
    transition: 'transform 0.3s ease',
    cursor: 'default'
  }} 
  className="card"
  onMouseEnter={(e) => {
    e.currentTarget.style.transform = 'translateY(-5px)';
  }}
  onMouseLeave={(e) => {
    e.currentTarget.style.transform = 'translateY(0)';
  }}
  >
    <span style={{ fontSize: '20px', marginRight: '10px' }}>{icon}</span>
    <span style={{ fontWeight: '500' }}>{text}</span>
  </div>
);

export default App;
