import { useAlerts } from "@/contexts/alerts";
import { API_URL, useAuth } from "@/contexts/auth";
import { useWebSocket } from "@/hooks/useWebSockets";
import { ApiClient } from "@/utility/api-client";
import { useEffect, useMemo } from "react";
import Teardrop from "./teardrop";
import { ColourToHex } from "@/utility/colour";
import { Box, CircularProgress, Stack, Typography } from "@mui/material";

type LiquidSensorProps = {
    room: string
}

export const LiquidSensor: React.FC<LiquidSensorProps> = ({ room }) => {
    const {token} = useAuth();
    const apiClient = useMemo(() => new ApiClient({baseUrl:`https://${API_URL}`}), [token]);
    const {lastMessage} = useWebSocket(apiClient, `/liquid/colour/subscribe?token=${token}&room=${room}`, );
    const { showAlert } = useAlerts();

    useEffect(() => {
        if(lastMessage && lastMessage.isBlood) {
           showAlert("Blood detected!", "error")
        }
    }, [lastMessage])

    if(lastMessage == null) {
        return <Box
            sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",     
            }}
                >
                <Stack spacing={2} alignItems="center">
                    <CircularProgress size={50} />
                    <Typography>Awaiting connection</Typography>
                </Stack>
            </Box>
    }

    return (<>
        <Teardrop value={50} size={70} colour={lastMessage ? ColourToHex(lastMessage) : undefined} />  
    </> 
    )
}