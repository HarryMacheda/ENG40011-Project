import React, { useEffect, useMemo } from "react";
import { PatientInfo } from "../utility/types";
import { Card, CardContent, Typography, Box } from "@mui/material";
import { useAuth } from "@/contexts/auth";
import { useWebSocket } from "@/hooks/useWebSockets";
import { ApiClient } from "@/utility/api-client";
import { useAlerts } from "@/contexts/alerts";
import { LiquidSensor } from "./liquidSensor";

interface PatientProps {
  patient: PatientInfo;
}

export const Patient: React.FC<PatientProps> = ({ patient }) => {
  const bloodColor = (bloodType: string) => {
    switch (bloodType) {
      case "A+": return "#f28b82";
      case "A-": return "#fbbc04";
      case "B+": return "#fff475";
      case "B-": return "#ccff90";
      case "O+": return "#a7ffeb";
      case "O-": return "#cbf0f8";
      case "AB+": return "#aecbfa";
      case "AB-": return "#d7aefb";
      default: return "#ffffff";
    }
  };

  return (
    <Card
      sx={{
        minWidth: 300,
        mb: 2,
        borderLeft: `8px solid ${bloodColor(patient.bloodType)}`,
        boxShadow: 3,
        transition: "transform 0.2s",
        "&:hover": { transform: "scale(1.03)" },
      }}
    >
      <CardContent sx={{ display: "flex", gap: 2 }}>
        {/* Left side: existing patient info */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" component="div" gutterBottom>
            {patient.firstName} <br/>
            {patient.lastName}
          </Typography>
          <Typography color="text.secondary">Room: {patient.room}</Typography>
          <Box
            mt={1}
            p={1}
            sx={{
              display: "inline-block",
              backgroundColor: bloodColor(patient.bloodType),
              borderRadius: 1,
              color: "#000",
              fontWeight: "bold",
            }}
          >
            {patient.bloodType}
          </Box>
        </Box>

        {/* Right side: placeholder for extra display */}
        <Box
          sx={{
            flexShrink: 0,
            width: 150, // fixed width for right-hand display
            borderLeft: "1px solid #ccc",
            pl: 2,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <LiquidSensor patient={patient}/>
        </Box>
      </CardContent>
    </Card>
  );
};
