import { useMemo, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';

export function useQueryParams<T>(paramKey: string, defaultValue: T) {
    const [searchParams, setSearchParams] = useSearchParams();

    // 1. Memoize the parsed value to avoid re-calculating on every render
    const value = useMemo(() => {
        const paramValue = searchParams.get(paramKey);

        // If the URL param doesn't exist, return the default value
        if (paramValue === null) {
            return defaultValue;
        }

        // Check the type of the defaultValue to decide how to parse the param
        switch (typeof defaultValue) {
            case 'number':
                const parsedInt = parseInt(paramValue, 10);
                // If parsing fails (e.g., "?count=abc"), fall back to the default
                return isNaN(parsedInt) ? defaultValue : (parsedInt as T);
            case 'boolean':
                // A simple convention for booleans
                return (paramValue === 'true') as T;
            case 'string':
            default:
                // For strings, just return the value directly
                return paramValue as T;
        }
    }, [searchParams, paramKey, defaultValue]);

    return { value, searchParams, setSearchParams };
}
