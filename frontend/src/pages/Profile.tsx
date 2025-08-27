import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Profile: React.FC = () => {
  // Mock user data since we bypassed authentication
  const mockUser = {
    full_name: 'Dr. John Faculty',
    email: 'john.faculty@university.edu',
    employee_id: 'FAC001',
    department: 'Computer Science',
    specialization: 'Machine Learning & AI',
    phone: '+1 234 567 8900',
    office: 'Block A, Room 301'
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Faculty Profile
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Personal Information
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>Name:</strong> {mockUser.full_name}
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>Email:</strong> {mockUser.email}
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>Employee ID:</strong> {mockUser.employee_id}
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>Department:</strong> {mockUser.department}
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>Specialization:</strong> {mockUser.specialization}
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>Phone:</strong> {mockUser.phone}
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>Office:</strong> {mockUser.office}
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Profile;
