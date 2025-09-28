

export type Colour = {
    r: number;
    g: number;
    b: number;
}

export const ColourToHex = (colour:Colour): string => {
    const toHex = (n: number) => {
        const hex = n.toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    }

    return `#${toHex(colour.r)}${toHex(colour.g)}${toHex(colour.b)}`;
} 

export const darkenHex = (hex: string, factor: number = 0.8): string => {
    hex = hex.replace(/^#/, '');

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);

    const newR = Math.max(0, Math.min(255, Math.floor(r * factor)));
    const newG = Math.max(0, Math.min(255, Math.floor(g * factor)));
    const newB = Math.max(0, Math.min(255, Math.floor(b * factor)));


    return ColourToHex({r:newR, g:newG, b:newB});
}
