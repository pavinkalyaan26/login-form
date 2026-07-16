import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function DashboardPage() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUserProfile = async () => {
      try {
        const response = await api.get('/profile');
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    };

    loadUserProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="page-shell">
      <div className="card dashboard-card">
        <h1>Dashboard</h1>
        <p className="subtitle">You are logged in successfully.</p>

        {user ? (
          <div className="profile-box">
            <p>
              <strong>Name:</strong> {user.name}
            </p>
            <p>
              <strong>Email:</strong> {user.email}
            </p>
            <p>
              <strong>Profile status:</strong> {user.age || user.gender || user.address || user.interests || user.bio ? 'Complete' : 'Incomplete'}
            </p>
          </div>
        ) : (
          <p>Loading profile...</p>
        )}

        <div className="button-row">
          <button className="secondary-btn" onClick={() => navigate('/profile')}>
            Edit profile details
          </button>
          <button className="primary-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
