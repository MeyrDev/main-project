

export function toStringOrNull(value: string): string | null {
    const trimmed = value.trim();

    return trimmed ? trimmed : null;
}

export function toNumberOrNull(value: string): number | null {
    if (!value.trim()) {
        return null;
    }

    return Number(value);
}

export function toNumber(value: string): number {
    return Number(value || 0);
}