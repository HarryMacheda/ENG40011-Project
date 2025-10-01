import { ApiClient } from "@/utility/api-client";
import { useWebSocket } from "@/hooks/useWebSockets";
import { useEffect, useMemo } from "react";
import { useAuth } from "@/contexts/auth";
import Teardrop from "@/components/teardrop";
import { Typography } from "@mui/material";
import { ColourToHex } from "@/utility/colour";
import { useAlerts } from "@/contexts/alerts";



export default function TeardropView() {
    const {token} = useAuth();
    const apiClient = useMemo(() => new ApiClient({baseUrl:"http://127.0.0.1:8000"}), [token]);
    const {lastMessage} = useWebSocket(apiClient, `/liquid/colour/subscribe?token=${token}`, );
    const { showAlert } = useAlerts();

    useEffect(() => {
        if(lastMessage && lastMessage.isBlood) {
           showAlert("Blood detected!", "error")
        }
    }, [lastMessage])

    return (<>
        <Teardrop value={50} size={500} colour={lastMessage ? ColourToHex(lastMessage) : undefined} />  
    </> 
    )
}
