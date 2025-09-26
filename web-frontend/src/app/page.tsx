"use client"
import React from "react";
import { Box, ThemeProvider } from "@mui/material";
import { AuthProvider } from "@/contexts/auth";
import theme from "@/theme";
import TeardropView from "./views/TeardropView";


export default function Home() {


  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <Box display="flex" flexDirection="column" alignItems="center" gap={4}>
          <TeardropView/>
        </Box>
      </AuthProvider>
    </ThemeProvider>
  );
}
