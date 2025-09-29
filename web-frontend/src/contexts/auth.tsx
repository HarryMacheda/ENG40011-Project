"use client"
import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { ApiClient } from "../utility/api-client";
import { Box, CircularProgress, Stack, Typography } from "@mui/material";

interface AuthContextType {
  token: string | null;
  error: string | null;
  login: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const apiClient = new ApiClient({ baseUrl: "http://127.0.0.1:8000"});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async () => {
    setLoading(true);
    setError(null);
    try {
        const formData = new FormData();
        formData.append("grant_type", "client_credentials");
        formData.append("client_id", "testing_connector");
        formData.append("client_secret", "1ee9435f3e8440299a96ce7853f01ec9");

        const data = await apiClient.request<{
            access_token: string;
            token_type: string;
            expires_in: number;
        }>("/auth/token", "POST", formData);

        setToken(data.access_token);
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {login()},[])

  if (loading) {
    return (
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 1300,
        }}
      >
        <Stack spacing={2}>
            <CircularProgress size={100} />
            <Typography>Authenticating...</Typography>
        </Stack>
      </Box>
    );
  }

  return (
    <AuthContext.Provider value={{ token, error, login }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
