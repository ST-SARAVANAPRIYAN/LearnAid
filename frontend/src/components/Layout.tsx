import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery,
  Paper,
  Divider,
  Button,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  People as PeopleIcon,
  Quiz as QuizIcon,
  Analytics as AnalyticsIcon,
  AccountCircle,
  Assessment as AssessmentIcon,
  Assignment as AssignmentIcon,
  Close as CloseIcon,
  TrendingUp,
  SwapHoriz as SwapIcon,
  AutoAwesome as AIIcon,
} from '@mui/icons-material';

const drawerWidth = 280;

const facultyMenuItems = [
  { text: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { text: 'Courses', path: '/courses', icon: <SchoolIcon /> },
  { text: 'Students', path: '/students', icon: <PeopleIcon /> },
  { text: 'Exams', path: '/exams', icon: <QuizIcon /> },
  { text: 'Tasks', path: '/tasks', icon: <AssignmentIcon /> },
  { text: 'AI Task Generation', path: '/task-generation', icon: <AIIcon /> },
  { text: 'Performance', path: '/performance', icon: <AssessmentIcon /> },
  { text: 'Analytics', path: '/analytics', icon: <AnalyticsIcon /> },
];

const studentMenuItems = [
  { text: 'Dashboard', path: '/student/dashboard', icon: <DashboardIcon /> },
  { text: 'My Courses', path: '/student/courses', icon: <SchoolIcon /> },
  { text: 'CIA Results', path: '/student/cia-results', icon: <QuizIcon /> },
  { text: 'My Tasks', path: '/student/tasks', icon: <AssignmentIcon /> },
  { text: 'Performance', path: '/student/performance', icon: <TrendingUp /> },
];

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  
  // Mock user role - in real app this would come from authentication
  const [userRole, setUserRole] = useState<'faculty' | 'student'>('faculty');

  const getMenuItems = () => {
    return userRole === 'student' ? studentMenuItems : facultyMenuItems;
  };

  const menuItems = getMenuItems();

  // Mock user data for development
  const userData = {
    faculty: {
      name: 'Dr. John Smith',
      email: 'john.smith@university.edu',
      department: 'Computer Science',
      role: 'Faculty'
    },
    student: {
      name: 'Alice Johnson', 
      email: 'alice.johnson@student.edu',
      department: 'Computer Science',
      studentId: 'CS21B001',
      role: 'Student'
    }
  };

  const currentUser = userRole === 'faculty' ? userData.faculty : userData.student;

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const drawer = (
    <Box>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 'bold',
              fontSize: '1.4rem',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
            }}
          >
            🎓
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main', lineHeight: 1 }}>
              LearnAid
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.75rem' }}>
              {userRole === 'faculty' ? 'Faculty Dashboard' : 'Student Dashboard'}
            </Typography>
          </Box>
          {isMobile && (
            <IconButton
              onClick={handleDrawerToggle}
              sx={{ color: 'text.secondary' }}
            >
              <CloseIcon />
            </IconButton>
          )}
        </Box>
      </Toolbar>
      
      <Divider sx={{ mx: 2 }} />
      
      <Box sx={{ p: 2 }}>
        <Paper
          elevation={0}
          sx={{
            p: 2,
            backgroundColor: 'primary.50',
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'primary.100',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar
              sx={{
                bgcolor: 'primary.main',
                width: 36,
                height: 36,
                fontSize: '0.875rem'
              }}
            >
              {currentUser.name.split(' ').map((n: string) => n[0]).join('')}
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                {currentUser.name}
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
                {currentUser.department}
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
      
      <List sx={{ px: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (isMobile) {
                  setMobileOpen(false);
                }
              }}
              sx={{
                borderRadius: 2,
                mx: 1,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                },
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: location.pathname === item.path ? 'white' : 'text.secondary',
                  minWidth: 40,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: '0.875rem',
                  fontWeight: location.pathname === item.path ? 600 : 400,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderBottom: '1px solid',
          borderColor: 'divider',
          backdropFilter: 'blur(8px)',
        }}
      >
        <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Box sx={{ flexGrow: 1 }}>
            <Typography 
              variant="h6" 
              noWrap 
              component="div" 
              sx={{ 
                fontWeight: 600,
                fontSize: { xs: '1.1rem', sm: '1.25rem' }
              }}
            >
              {userRole === 'faculty' ? 'Faculty Dashboard' : 'Student Dashboard'}
            </Typography>
            <Typography 
              variant="caption" 
              sx={{ 
                opacity: 0.8,
                display: { xs: 'none', sm: 'block' }
              }}
            >
              LearnAid - Intelligent Learning System
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Role Switcher for Development */}
            <Tooltip title={`Switch to ${userRole === 'faculty' ? 'Student' : 'Faculty'} View`}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<SwapIcon />}
                onClick={() => {
                  const newRole = userRole === 'faculty' ? 'student' : 'faculty';
                  setUserRole(newRole);
                  // Navigate to appropriate dashboard
                  navigate(newRole === 'student' ? '/student/dashboard' : '/dashboard');
                }}
                sx={{ 
                  color: 'white', 
                  borderColor: 'rgba(255,255,255,0.3)',
                  '&:hover': { 
                    borderColor: 'rgba(255,255,255,0.6)',
                    backgroundColor: 'rgba(255,255,255,0.1)'
                  },
                  display: { xs: 'none', sm: 'flex' }
                }}
              >
                {userRole === 'faculty' ? 'Student' : 'Faculty'}
              </Button>
            </Tooltip>
            
            <Typography 
              variant="body2" 
              sx={{ 
                display: { xs: 'none', md: 'block' },
                fontWeight: 500 
              }}
            >
              {currentUser.name}
            </Typography>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleProfileMenuOpen}
              color="inherit"
              sx={{ 
                p: { xs: 0.5, sm: 1 },
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' }
              }}
            >
              <Avatar 
                sx={{ 
                  width: { xs: 32, sm: 36 }, 
                  height: { xs: 32, sm: 36 },
                  bgcolor: 'rgba(255,255,255,0.2)',
                  fontSize: '0.875rem'
                }}
              >
                {currentUser.name.split(' ').map(n => n[0]).join('')}
              </Avatar>
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleProfileMenuClose}
              sx={{
                mt: 1,
                '& .MuiPaper-root': {
                  borderRadius: 2,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                }
              }}
            >
              <MenuItem 
                onClick={handleProfileMenuClose}
                sx={{ minWidth: 150, gap: 2 }}
              >
                <AccountCircle fontSize="small" />
                Profile
              </MenuItem>
              <MenuItem 
                onClick={() => {
                  handleProfileMenuClose();
                  console.log('Logout - Development Mode');
                }}
                sx={{ minWidth: 150, gap: 2 }}
              >
                <Box component="span" sx={{ fontSize: 20 }}>🚪</Box>
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="navigation menu"
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              backgroundImage: 'none',
              backgroundColor: 'background.paper',
            },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              borderRight: '1px solid',
              borderColor: 'divider',
              backgroundImage: 'none',
              backgroundColor: 'background.paper',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{ 
          flexGrow: 1, 
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: 'background.default',
          position: 'relative',
        }}
      >
        {/* Content area with proper spacing */}
        <Box
          sx={{
            p: { xs: 2, sm: 3 },
            mt: { xs: 7, sm: 8 }, // Account for AppBar height
            minHeight: 'calc(100vh - 64px)',
            maxWidth: '100%',
            overflow: 'hidden',
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;
