import { ApiClient } from "@/utility/api-client";
import { useWebSocket } from "@/hooks/useWebSockets";
import { useMemo } from "react";
import { useAuth } from "@/contexts/auth";
import Teardrop from "@/components/teardrop";
import { Typography } from "@mui/material";
import { ColourToHex } from "@/utility/colour";



export default function TeardropView() {
    const {token} = useAuth();
    const apiClient = useMemo(() => new ApiClient({baseUrl:"http://127.0.0.1:8000"}), [token]);
    const {isConnected, lastMessage} = useWebSocket<any>(apiClient, `/liquid/colour/subscribe?token=${token}`, );

    return (<>
        <Teardrop value={50} size={500} colour={lastMessage ? ColourToHex(lastMessage) : undefined} />  
    </> 
    )
}
