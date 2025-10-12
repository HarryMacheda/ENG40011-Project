"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import { ApiClient } from "../utility/api-client";
import { Box, CircularProgress, Stack, Typography, TextField, Button } from "@mui/material";
import { Capacitor } from "@capacitor/core";

interface AuthContextType {
  token: string | null;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const API_URL = Capacitor.isNativePlatform() ? "10.0.2.2:8000" : "127.0.0.1:8000";
const apiClient = new ApiClient({ baseUrl: `https://${API_URL}` });

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const data = await apiClient.request<{
        access_token: string;
        token_type: string;
        expires_in?: number;
      }>("/auth/token-password", "POST", formData);

      setToken(data.access_token);
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const [usernameInput, setUsernameInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");

  if (!token) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        {loading ? (
          <Stack spacing={2} alignItems="center">
            <CircularProgress size={100} />
            <Typography>Authenticating...</Typography>
          </Stack>
        ) : (
          <Stack spacing={2} width={300}>
            <Typography variant="h6">Login</Typography>
            <TextField
              label="Username"
              value={usernameInput}
              onChange={(e) => setUsernameInput(e.target.value)}
              fullWidth
              variant="filled"
            />
            <TextField
              label="Password"
              type="password"
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              fullWidth
              variant="filled"
            />
            {error && (
              <Typography color="error" variant="body2">
                Invalid username or password
              </Typography>
            )}
            <Button
              variant="contained"
              onClick={() => login(usernameInput, passwordInput)}
            >
              Login
            </Button>
          </Stack>
        )}
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
