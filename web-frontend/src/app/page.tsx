"use client"
import React from "react";
import { Box, Button, ThemeProvider } from "@mui/material";
import { AuthProvider } from "@/contexts/auth";
import theme from "@/theme";
import TeardropView from "./views/TeardropView";
import { AlertsProvider } from "@/contexts/alerts";
import AllPatients from "./views/AllPatients";


export default function Home() {


  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <AlertsProvider>
          <Box width={"100%"} height={"100%"}>
            <Box display="flex" flexDirection="column" alignItems="center" gap={4} justifyContent={"center"} height={"100%"}>
              <AllPatients/>
            </Box>
          </Box>
        </AlertsProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}