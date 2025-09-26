"use client"
import React from "react";
import { Box, Button, ThemeProvider } from "@mui/material";
import { AuthProvider } from "@/contexts/auth";
import theme from "@/theme";
import TeardropView from "./views/TeardropView";
import { AlertsProvider } from "@/contexts/alerts";


export default function Home() {


  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <AlertsProvider>
          <Box display="flex" flexDirection="column" alignItems="center" gap={4}>
            <TeardropView/>
          </Box>
        </AlertsProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}