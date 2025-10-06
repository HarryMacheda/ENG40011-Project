import React from "react";
import { Dialog, DialogTitle, DialogContent, Typography, Box, Button } from "@mui/material";
import { PatientInfo } from "../utility/types";

interface PatientDialogProps {
  patient: PatientInfo;
  open: boolean;
  onClose?: () => void;
}

export const PatientDialog: React.FC<PatientDialogProps> = ({ patient, open, onClose }) => {
  const bloodColor = (type: string) => {
    switch (type) {
      case "A+": return "#ff9999";
      case "B+": return "#ffcc99";
      case "AB+": return "#cc99ff";
      case "O+": return "#99ccff";
      default: return "#ccc";
    }
  };

  const handleClose = () => {
    if (onClose) onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {patient.firstName} {patient.lastName} — Room {patient.room}
      </DialogTitle>
      <DialogContent dividers>
        <Typography variant="body1">Blood type: {patient.bloodType}</Typography>

        <Box
          mt={2}
          p={1}
          sx={{
            borderLeft: `4px solid ${bloodColor(patient.bloodType)}`,
            pl: 2,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            LIQUID DETECTED
          </Typography>
        </Box>

        <Box mt={2}>
          <Button variant="contained" onClick={handleClose}>
            Close
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
};
