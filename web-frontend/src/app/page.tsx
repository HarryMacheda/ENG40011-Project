"use client"
import Teardrop from "@/components/teardrop";
import React, { useState } from "react";
import { Box, Slider, Typography } from "@mui/material";

export default function Home() {
  const [value, setValue] = useState(50);

  return (
    <Box display="flex" flexDirection="column" alignItems="center" gap={4}>
      <Teardrop value={value} size={500} />

      <Box width={300}>
        <Typography gutterBottom>Fill Level</Typography>
        <Slider
          value={value}
          onChange={(e, newValue) => setValue(newValue)}
          step={1}
          min={0}
          max={100}
          valueLabelDisplay="auto"
        />
      </Box>
    </Box>
  );
}
