import React from 'react';

interface PrivateRouteProps {
  children: React.ReactNode;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  // Development mode - skip all authentication
  // TODO: Implement proper authentication before production
  return <>{children}</>;
};

export default PrivateRoute;
