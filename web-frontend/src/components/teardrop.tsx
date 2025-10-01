import React from "react";
import { Box, Typography } from "@mui/material";
import { darkenHex } from "@/utility/colour";


export default function Teardrop({ value = 50, size = 150, colour="#121212"}) {
  const safeValue = Math.min(Math.max(value, 0), 100);

  const fillHeight = (safeValue / 100) * 125;
  const y = 130 - fillHeight;

  return (
    <Box display="flex" flexDirection="column" alignItems="center">
      <svg
        width={size}
        height={size * 1.3}
        viewBox="0 0 100 130"
        xmlns="http://www.w3.org/2000/svg"
        style={{ overflow: "visible" }}
      >
        <path
          d="M50 5 C20 55, 5 80, 25 110 Q50 140, 75 110 C95 80, 80 55, 50 5 Z"
          fill="#121212"
          stroke="#ffffff"
          strokeWidth="2"
        />

        <clipPath id="teardrop-clip">
          <path d="M50 5 C20 55, 5 80, 25 110 Q50 140, 75 110 C95 80, 80 55, 50 5 Z" />
        </clipPath>

        <path
          d={`M0 ${y} Q25 ${y + 7}, 50 ${y} T100 ${y} V130 H0 Z`}
          fill={darkenHex(colour)}
          clipPath="url(#teardrop-clip)"
        />
        <path
          d={`M0 ${y} Q25 ${y - 15}, 50 ${y} T100 ${y} V130 H0 Z`}
          fill={colour}
          clipPath="url(#teardrop-clip)"
        />

        <path
          d="M50 5 C20 55, 5 80, 25 110 Q50 140, 75 110 C95 80, 80 55, 50 5 Z"
          fill="None"
          stroke="#ffffff"
          strokeWidth="2"
        />
      </svg>

      <Typography variant="h6" mt={1}>
        {(2 * (safeValue / 100)) * 1000} ml
      </Typography>
    </Box>
  );
}
