// AlertsContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Snackbar, Alert as MuiAlert, AlertColor } from '@mui/material';

type Alert = {
  message: string;
  severity: AlertColor; // 'error' | 'warning' | 'info' | 'success'
};

type AlertsContextType = {
  showAlert: (message: string, severity?: AlertColor) => void;
};

const AlertsContext = createContext<AlertsContextType | undefined>(undefined);

export const AlertsProvider = ({ children }: { children: ReactNode }) => {
  const [alert, setAlert] = useState<Alert | null>(null);
  const [open, setOpen] = useState(false);

  const showAlert = (message: string, severity: AlertColor = 'info') => {
    setAlert({ message, severity });
    setOpen(true);
  };

  const handleClose = (_?: any, reason?: string) => {
    if (reason === 'clickaway') return;
    setOpen(false);
  };

  return (
    <AlertsContext.Provider value={{ showAlert }}>
      {children}
      {alert && (
        <Snackbar 
            open={open} 
            autoHideDuration={3000} 
            onClose={handleClose}
            anchorOrigin={{ vertical:"top", horizontal:"center" }}
        >
          <MuiAlert 
            onClose={handleClose} 
            severity={alert.severity} 
            sx={{ width: '100%' }}
            variant='filled'
          >
            {alert.message}
          </MuiAlert>
        </Snackbar>
      )}
    </AlertsContext.Provider>
  );
};

export const useAlerts = (): AlertsContextType => {
  const context = useContext(AlertsContext);
  if (!context) {
    throw new Error('useAlerts must be used within an AlertsProvider');
  }
  return context;
};
