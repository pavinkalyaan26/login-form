import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function ProfilePage() {
  const [profile, setProfile] = useState({
    name: '',
    age: '',
    gender: '',
    address: '',
    interests: '',
    bio: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const navigate = useNavigate();

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await api.get('/profile');
        const data = response.data;
        setProfile({
          name: data.name || '',
          age: data.age || '',
          gender: data.gender || '',
          address: data.address || '',
          interests: data.interests || '',
          bio: data.bio || '',
        });
      } catch (error) {
        localStorage.removeItem('token');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setProfile((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleSave = async (event) => {
    event.preventDefault();
    setMessage({ type: '', text: '' });
    setSaving(true);

    try {
      const payload = {
        name: profile.name,
        age: profile.age ? Number(profile.age) : null,
        gender: profile.gender,
        address: profile.address,
        interests: profile.interests,
        bio: profile.bio,
      };
      const response = await api.put('/profile', payload);
      const updated = response.data;
      setProfile({
        name: updated.name || '',
        age: updated.age ?? '',
        gender: updated.gender || '',
        address: updated.address || '',
        interests: updated.interests || '',
        bio: updated.bio || '',
      });
      setMessage({ type: 'success', text: 'Profile saved successfully.' });
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Could not save profile.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="page-shell">
        <div className="card">
          <p>Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-shell">
      <div className="card profile-card">
        <h1>Profile Details</h1>
        <p className="subtitle">Add or edit your personal information anytime.</p>

        {message.text && <div className={`message ${message.type}`}>{message.text}</div>}

        <form onSubmit={handleSave}>
          <div className="field">
            <label>Name</label>
            <input name="name" value={profile.name} onChange={handleChange} placeholder="Your name" />
          </div>

          <div className="field">
            <label>Age</label>
            <input name="age" type="number" value={profile.age} onChange={handleChange} placeholder="Your age" />
          </div>

          <div className="field">
            <label>Gender</label>
            <input name="gender" value={profile.gender} onChange={handleChange} placeholder="Gender" />
          </div>

          <div className="field">
            <label>Address</label>
            <input name="address" value={profile.address} onChange={handleChange} placeholder="Address" />
          </div>

          <div className="field">
            <label>Interests</label>
            <input name="interests" value={profile.interests} onChange={handleChange} placeholder="Interests" />
          </div>

          <div className="field">
            <label>Short bio</label>
            <textarea name="bio" value={profile.bio} onChange={handleChange} placeholder="Write a short bio" />
          </div>

          <div className="button-row">
            <button className="primary-btn" type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save profile'}
            </button>
            <button className="secondary-btn" type="button" onClick={() => navigate('/dashboard')}>
              Back to dashboard
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ProfilePage;
