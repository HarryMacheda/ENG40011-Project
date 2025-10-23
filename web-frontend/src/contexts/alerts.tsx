// AlertsContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  AlertColor,
  Box,
  Typography,
} from '@mui/material';
import { keyframes } from '@emotion/react';

type Alert = {
  title?: string;
  message: ReactNode;
  severity: AlertColor; // 'error' | 'warning' | 'info' | 'success'
};

type AlertsContextType = {
  showAlert: (message: ReactNode, severity?: AlertColor, title?: string) => void;
  closeAlert: () => void;
};

const AlertsContext = createContext<AlertsContextType | undefined>(undefined);

const flashRed = keyframes`
  0%, 100% { background-color: #ffb3b3; } 
  50% { background-color: #ff0000; }
`;

export const AlertsProvider = ({ children }: { children: ReactNode }) => {
  const [alert, setAlert] = useState<Alert | null>(null);
  const [open, setOpen] = useState(false);

  const showAlert = (
    message: ReactNode,
    severity: AlertColor = 'info',
    title?: string
  ) => {
    setAlert({ message, severity, title });
    setOpen(true);
  };

  const closeAlert = () => {
    setOpen(false);
  };

  return (
    <AlertsContext.Provider value={{ showAlert, closeAlert }}>
      {children}

      {alert && (
        <Dialog
          open={open}
          onClose={closeAlert}
          fullWidth
          maxWidth="sm"
          PaperProps={{
            sx: {
              animation: alert.severity === 'error' ? `${flashRed} 1s infinite` : undefined,
              backgroundColor: 'background.paper',
              borderRadius: 3,
              p: 2,
              boxShadow: 6,
            },
          }}
        >
          {alert.title && (
            <DialogTitle
              sx={{
                color: "#FFFFFF",
                fontSize: "2rem",            
                fontWeight: 'bold',
              }}
            >
              {alert.title}
            </DialogTitle>
          )}

          <DialogContent>
            {typeof alert.message === 'string' ? (
              <Typography>{alert.message}</Typography>
            ) : (
              alert.message
            )}
          </DialogContent>

          <DialogActions>
            <Button
              variant="contained"
              color={
                alert.severity === 'error'
                  ? 'error'
                  : alert.severity === 'warning'
                  ? 'warning'
                  : alert.severity === 'success'
                  ? 'success'
                  : 'info'
              }
              onClick={closeAlert}
            >
              OK
            </Button>
          </DialogActions>
        </Dialog>
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
