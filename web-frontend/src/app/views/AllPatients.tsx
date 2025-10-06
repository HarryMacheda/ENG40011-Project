"use client"
import { ApiClient } from "@/utility/api-client";
import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/contexts/auth";
import Teardrop from "@/components/teardrop";
import { Box, CircularProgress, Container, Grid, List, ListItem, ListItemText, Stack, Typography } from "@mui/material";
import { ColourToHex } from "@/utility/colour";
import { useAlerts } from "@/contexts/alerts";
import { PatientInfo } from "@/utility/types";
import { Patient } from "@/components/patient";
import { PatientDialog } from "@/components/PatientDialog";
import { useWebSocket } from "@/hooks/useWebSockets";


export default function AllPatients() { 
    const {token} = useAuth();
    const apiClient = useMemo(() => new ApiClient({baseUrl:"http://127.0.0.1:8000", headers:{"Authorization":`Bearer ${token}`}}), [token]);
    const [patients, setPatients] = useState<PatientInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const {lastMessage} = useWebSocket(apiClient, `/liquid/detected/subscribe?token=${token}` );
    const [open, setOpen] = useState(false);


    useEffect(() => {
        const fetchPatients = async () => {
            try {
                setLoading(true);
                const data = await apiClient.request<PatientInfo[]>("/patients/", "GET");
                setPatients(data);
            } catch (err: any) {
            } finally {
                setLoading(false);
            }
        };

        fetchPatients();
    }, []); 
    
    useEffect(() => {
        setOpen(true);
    }, [lastMessage]);

    if(loading || token == null) {
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
                    <Typography>Loading Patients</Typography>
                </Stack>
            </Box>
        )
    }

    return (<>
        <Container sx={{ padding: 1, width:"100%", margin:0, maxWidth:"100% !important" }}>
            <Grid container spacing={2}>
                {patients.map((p) => (
                    <Grid size={3} key={p.room}>
                        <Patient patient={p} />
                    </Grid>
                ))}
            </Grid>
        </Container>
        {lastMessage && <PatientDialog patient={patients.find(x => x.room == lastMessage.room)!!} open={open} onClose={() => setOpen(false)}/> }
    </>
    )
}
